import pytest
import database


def test_add_booking_returns_true_new_row_id():
    """Verify add_booking returns positive, sequentially increasing row IDs."""
    assert database.add_user(
        "testuser", "password123", "test@example.com", "Test User", "1234567890"
    )
    user = database.authenticate_user("testuser", "password123")
    assert user is not None
    user_id = user["id"]

    id1 = database.add_booking(
        user_id=user_id,
        customer_name="Customer One",
        destination_name="Goa",
        package_type="Silver",
        travel_date="01/01/2027",
        number_of_people=1,
        total_price=15000.0,
    )
    id2 = database.add_booking(
        user_id=user_id,
        customer_name="Customer Two",
        destination_name="Mumbai",
        package_type="Golden",
        travel_date="02/02/2027",
        number_of_people=2,
        total_price=36000.0,
    )

    assert id1 is not None and id1 > 0, f"Expected valid positive ID, got {id1}"
    assert id2 is not None and id2 > id1, f"Expected second booking ID ({id2}) > first booking ID ({id1})"


def test_create_trip_plan_returns_true_new_row_id():
    """Verify create_trip_plan returns positive, sequentially increasing row IDs."""
    assert database.add_user(
        "planner_user", "password123", "planner@example.com", "Planner User", "1234567890"
    )
    user = database.authenticate_user("planner_user", "password123")
    assert user is not None
    user_id = user["id"]

    plan1 = database.create_trip_plan(
        user_id=user_id,
        plan_name="Trip 1",
        budget=10000.0,
    )
    plan2 = database.create_trip_plan(
        user_id=user_id,
        plan_name="Trip 2",
        budget=20000.0,
    )

    assert plan1 is not None and plan1 > 0, f"Expected valid positive ID, got {plan1}"
    assert plan2 is not None and plan2 > plan1, f"Expected second plan ID ({plan2}) > first plan ID ({plan1})"
