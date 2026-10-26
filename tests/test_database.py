import pytest
import database


# 1. Password Hashing and Verification
def test_password_hashing_and_verification():
    raw_password = "SecurePassword123!"
    hashed = database.hash_password(raw_password)

    # Check format: salt$hash
    assert "$" in hashed
    parts = hashed.split("$")
    assert len(parts) == 2
    salt, hash_hex = parts
    assert len(salt) == 32  # 16-byte hex
    assert len(hash_hex) == 64  # sha256 hex is 64 chars

    # Correct password verifies
    assert database.verify_password(hashed, raw_password) is True

    # Wrong password fails
    assert database.verify_password(hashed, "WrongPassword") is False

    # Invalid stored hash format returns False safely
    assert database.verify_password("invalidhashwithoutdollar", raw_password) is False


# 2. User Registration and Duplicate Username Prevention
def test_user_registration_and_duplicate():
    # Successful registration
    assert database.add_user(
        username="johndoe",
        password="password123",
        email="john@example.com",
        full_name="John Doe",
        phone="9876543210",
    ) is True

    # Duplicate username must fail
    assert database.add_user(
        username="johndoe",
        password="differentpassword",
        email="another@example.com",
        full_name="Another Name",
        phone="1122334455",
    ) is False


# 3. Authentication
def test_user_authentication():
    username = "authtest"
    password = "MySecretPassword"
    database.add_user(
        username=username,
        password=password,
        email="auth@example.com",
        full_name="Auth Tester",
        phone="5551234567",
    )

    # Valid credentials return user dictionary
    user = database.authenticate_user(username, password)
    assert user is not None
    assert user["username"] == username
    assert user["email"] == "auth@example.com"
    assert user["full_name"] == "Auth Tester"
    assert "password_hash" in user

    # Invalid password returns None
    assert database.authenticate_user(username, "BadPassword") is None

    # Nonexistent user returns None
    assert database.authenticate_user("ghost_user", password) is None


# 4. Package Pricing Calculation
@pytest.mark.parametrize(
    "package_type, base_price, people, expected_total",
    [
        ("Silver", 1000.0, 1, 1000.0),
        ("Silver", 1000.0, 3, 3000.0),
        ("Golden", 1000.0, 1, 1500.0),
        ("Golden", 1000.0, 2, 3000.0),
        ("Diamond", 1000.0, 1, 2000.0),
        ("Diamond", 1000.0, 4, 8000.0),
        ("UnknownPackage", 1000.0, 2, 2000.0),  # Defaults to 1.0 multiplier
    ],
)
def test_calculate_package_price(package_type, base_price, people, expected_total):
    result = database.calculate_package_price(base_price, package_type, people)
    assert result == pytest.approx(expected_total)


# 5. Destination Search and Filters
def test_destination_search_filters():
    # Keyword search by name
    goa_results = database.search_destinations(query="Goa")
    assert len(goa_results) == 1
    assert goa_results[0]["name"] == "Goa"

    # Keyword search by description (e.g. "Bollywood" in Mumbai description)
    mumbai_results = database.search_destinations(query="Bollywood")
    assert any(d["name"] == "Mumbai" for d in mumbai_results)

    # Category filter
    mountains = database.search_destinations(category="Mountain")
    mountain_names = {d["name"] for d in mountains}
    assert "Sikkim" in mountain_names
    assert "Manali" in mountain_names
    assert "Goa" not in mountain_names

    # Budget filter (base_price <= 15000)
    # Sample prices: Mumbai=12000, Kerala=14000, Goa=15000, Manali=16000, Sikkim=18000, Rajasthan=20000
    affordable = database.search_destinations(max_price=15000.0)
    affordable_names = {d["name"] for d in affordable}
    assert "Mumbai" in affordable_names
    assert "Kerala" in affordable_names
    assert "Goa" in affordable_names
    assert "Sikkim" not in affordable_names
    assert "Rajasthan" not in affordable_names

    # Combined filter: Mountain and max_price <= 17000 (Manali is 16000, Sikkim is 18000)
    filtered = database.search_destinations(category="Mountain", max_price=17000.0)
    filtered_names = [d["name"] for d in filtered]
    assert "Manali" in filtered_names
    assert "Sikkim" not in filtered_names


@pytest.mark.xfail(
    reason="GAP-009: Tag search query uses SQL 'IN' which cannot match comma-delimited string fields"
)
def test_destination_tag_search():
    # Destinations store tags as "beach,party,relaxation"
    results = database.search_destinations(tags=["beach"])
    assert len(results) > 0


# 6. Booking Creation and Cancellation
def test_booking_creation_and_cancellation():
    database.add_user("booker", "pass", "booker@test.com", "Booker User")
    user = database.authenticate_user("booker", "pass")
    user_id = user["id"]

    booking_id = database.add_booking(
        user_id=user_id,
        customer_name="Booker User",
        destination_name="Goa",
        package_type="Diamond",
        travel_date="15/12/2026",
        number_of_people=2,
        total_price=60000.0,
    )
    assert booking_id is not None and booking_id > 0

    # Verify booking exists with initial status 'confirmed'
    booking = database.get_booking_by_id(booking_id)
    assert booking is not None
    assert booking["status"] == "confirmed"
    assert booking["package_type"] == "Diamond"
    assert booking["number_of_people"] == 2
    assert booking["total_price"] == 60000.0

    # Cancel booking
    assert database.update_booking_status(booking_id, "cancelled") is True
    updated_booking = database.get_booking_by_id(booking_id)
    assert updated_booking["status"] == "cancelled"


# 7. Review Rating Average Update
def test_review_rating_average_update():
    database.add_user("reviewer1", "pass", "r1@test.com", "R1")
    database.add_user("reviewer2", "pass", "r2@test.com", "R2")
    u1 = database.authenticate_user("reviewer1", "pass")
    u2 = database.authenticate_user("reviewer2", "pass")

    destinations = database.search_destinations(query="Goa")
    assert len(destinations) > 0
    dest_id = destinations[0]["id"]

    # First review: 4 stars
    assert database.add_review(u1["id"], dest_id, rating=4, comment="Great trip!") is True
    dest_after_1 = database.get_destination_by_id(dest_id)
    assert dest_after_1["rating"] == 4.0

    # Second review: 5 stars (average of 4 and 5 is 4.5)
    assert database.add_review(u2["id"], dest_id, rating=5, comment="Amazing beaches!") is True
    dest_after_2 = database.get_destination_by_id(dest_id)
    assert dest_after_2["rating"] == 4.5


# 8. Export User Data Keys
def test_export_user_data_keys():
    database.add_user("exporter", "pass", "exporter@test.com", "Export User")
    user = database.authenticate_user("exporter", "pass")
    user_id = user["id"]

    data = database.export_user_data(user_id)
    assert isinstance(data, dict)
    expected_keys = {"user_info", "bookings", "trip_plans", "reviews", "exported_at"}
    assert expected_keys.issubset(data.keys())
    assert data["user_info"]["username"] == "exporter"
    assert isinstance(data["bookings"], list)
    assert isinstance(data["trip_plans"], list)
    assert isinstance(data["reviews"], list)
