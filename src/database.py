"""
Database module for Travel Management System.
Provides improved database architecture with helper classes and parameterized queries.
"""

import sqlite3
import os
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "travel.db")


class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass


class DatabaseManager:
    """Centralized database manager with improved architecture."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    def execute(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Execute a query and return single result."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchone()
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT query and return the last inserted row ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute a query with multiple parameter sets."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Fetch all results from a query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch single result from a query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()


# Global database manager instance
db = DatabaseManager()


def set_database_path(new_path: Optional[str] = None) -> str:
    """Set the database path for DatabaseManager and module operations."""
    global DATABASE_PATH
    if new_path is not None:
        DATABASE_PATH = new_path
    else:
        DATABASE_PATH = os.path.join(BASE_DIR, "database", "travel.db")
    db.db_path = DATABASE_PATH
    db._ensure_db_directory()
    return DATABASE_PATH


def hash_password(password: str) -> str:
    """Hash password with salt for secure storage."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"


def verify_password(stored: str, provided: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, hashed = stored.split('$')
        provided_hash = hashlib.pbkdf2_hmac('sha256', provided.encode(), salt.encode(), 100000)
        return provided_hash.hex() == hashed
    except:
        return False


def init_database():
    """Initialize database with all required tables."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Users table with improved schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                full_name TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Destinations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS destinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                base_price REAL,
                rating REAL DEFAULT 0.0,
                image_path TEXT,
                tags TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Bookings table with improved schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                destination_id INTEGER,
                customer_name TEXT NOT NULL,
                customer_age INTEGER,
                customer_phone TEXT,
                customer_address TEXT,
                destination_name TEXT,
                package_type TEXT,
                travel_date TEXT,
                number_of_people INTEGER DEFAULT 1,
                total_price REAL,
                status TEXT DEFAULT 'pending',
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (destination_id) REFERENCES destinations (id)
            )
        """)
        
        # Reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                destination_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (destination_id) REFERENCES destinations (id)
            )
        """)
        
        # Trip plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trip_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                destination_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (destination_id) REFERENCES destinations (id)
            )
        """)
        
        # User preferences table for recommendations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preferred_category TEXT,
                budget_range_min REAL,
                budget_range_max REAL,
                preferred_destinations TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
    
    # Add sample data
    add_sample_data()


def add_sample_data():
    """Add sample data if database is empty."""
    # Check if destinations exist
    existing = db.fetch_all("SELECT COUNT(*) as count FROM destinations")
    if existing and existing[0]['count'] > 0:
        return
    
    # Sample destinations
    destinations = [
        ("Goa", "Beautiful beaches, vibrant nightlife, and Portuguese heritage.", "Beach", 15000.0, "Goa/goa-1.jpg", "beach,party,relaxation"),
        ("Mumbai", "The city of dreams - Bollywood, beaches, and iconic landmarks.", "City", 12000.0, "Mumbai/mumbai-1.jpg", "city,culture,shopping"),
        ("Sikkim", "Majestic mountains, monasteries, and pristine nature.", "Mountain", 18000.0, "Sikkim/sikkim-1.jpg", "mountain,adventure,nature"),
        ("Kerala", "Backwaters, tea plantations, and serene landscapes.", "Nature", 14000.0, None, "nature,relaxation,backwaters"),
        ("Rajasthan", "Royal palaces, deserts, and rich cultural heritage.", "Heritage", 20000.0, None, "heritage,culture,desert"),
        ("Manali", "Snow-capped mountains, adventure sports, and scenic beauty.", "Mountain", 16000.0, None, "mountain,adventure,snow"),
    ]
    
    db.execute_many(
        "INSERT INTO destinations (name, description, category, base_price, image_path, tags) VALUES (?, ?, ?, ?, ?, ?)",
        destinations
    )
    
    print("Sample destinations added successfully!")


# ==================== USER OPERATIONS ====================

def add_user(username: str, password: str, email: str = None, full_name: str = None, phone: str = None) -> bool:
    """Add a new user with hashed password."""
    try:
        password_hash = hash_password(password)
        db.execute(
            """
            INSERT INTO users (username, password_hash, email, full_name, phone)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, password_hash, email, full_name, phone)
        )
        return True
    except DatabaseError:
        return False


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user and return user data if successful."""
    user = db.fetch_one(
        "SELECT * FROM users WHERE username = ? AND is_active = 1",
        (username,)
    )
    
    if user and verify_password(user['password_hash'], password):
        # Update last login
        db.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        return dict(user)
    return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    user = db.fetch_one(
        "SELECT id, username, email, full_name, phone, created_at FROM users WHERE id = ?",
        (user_id,)
    )
    return dict(user) if user else None


def update_user(user_id: int, **kwargs) -> bool:
    """Update user information."""
    allowed_fields = ['email', 'full_name', 'phone']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [user_id]
    
    try:
        db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", tuple(values))
        return True
    except DatabaseError:
        return False


# ==================== DESTINATION OPERATIONS ====================

def get_all_destinations(active_only: bool = True) -> List[Dict[str, Any]]:
    """Get all destinations."""
    query = "SELECT * FROM destinations"
    if active_only:
        query += " WHERE is_active = 1"
    
    rows = db.fetch_all(query)
    return [dict(row) for row in rows]


def get_destination_by_id(destination_id: int) -> Optional[Dict[str, Any]]:
    """Get destination by ID."""
    row = db.fetch_one(
        "SELECT * FROM destinations WHERE id = ?",
        (destination_id,)
    )
    return dict(row) if row else None


def search_destinations(
    query: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    tags: List[str] = None
) -> List[Dict[str, Any]]:
    """Search destinations with filters."""
    sql = "SELECT * FROM destinations WHERE is_active = 1"
    params = []
    
    if query:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    
    if category:
        sql += " AND category = ?"
        params.append(category)
    
    if min_price is not None:
        sql += " AND base_price >= ?"
        params.append(min_price)
    
    if max_price is not None:
        sql += " AND base_price <= ?"
        params.append(max_price)
    
    if tags:
        placeholders = ', '.join('?' * len(tags))
        sql += f" AND tags IN ({placeholders})"
        params.extend(tags)
    
    rows = db.fetch_all(sql, tuple(params))
    return [dict(row) for row in rows]


def get_destination_categories() -> List[str]:
    """Get all unique destination categories."""
    rows = db.fetch_all(
        "SELECT DISTINCT category FROM destinations WHERE is_active = 1 ORDER BY category"
    )
    return [row['category'] for row in rows]


# ==================== BOOKING OPERATIONS ====================

def add_booking(
    user_id: int,
    customer_name: str,
    destination_name: str,
    package_type: str,
    travel_date: str,
    number_of_people: int = 1,
    customer_age: int = None,
    customer_phone: str = None,
    customer_address: str = None,
    destination_id: int = None,
    total_price: float = None
) -> Optional[int]:
    """Add a new booking and return booking ID."""
    try:
        booking_id = db.execute_insert(
            """
            INSERT INTO bookings (
                user_id, destination_id, customer_name, customer_age, customer_phone,
                customer_address, destination_name, package_type, travel_date,
                number_of_people, total_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, destination_id, customer_name, customer_age, customer_phone,
             customer_address, destination_name, package_type, travel_date,
             number_of_people, total_price, 'confirmed')
        )
        return booking_id
    except DatabaseError as e:
        print(f"Error adding booking: {e}")
        return None


def get_user_bookings(user_id: int) -> List[Dict[str, Any]]:
    """Get all bookings for a user."""
    rows = db.fetch_all(
        """
        SELECT b.*, d.name as destination_display_name, d.image_path
        FROM bookings b
        LEFT JOIN destinations d ON b.destination_id = d.id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC
        """,
        (user_id,)
    )
    return [dict(row) for row in rows]


def get_all_bookings() -> List[Dict[str, Any]]:
    """Get all bookings (for admin)."""
    rows = db.fetch_all(
        """
        SELECT b.*, u.username, d.name as destination_display_name
        FROM bookings b
        LEFT JOIN users u ON b.user_id = u.id
        LEFT JOIN destinations d ON b.destination_id = d.id
        ORDER BY b.booking_date DESC
        """
    )
    return [dict(row) for row in rows]


def get_booking_by_id(booking_id: int) -> Optional[Dict[str, Any]]:
    """Get booking by ID."""
    row = db.fetch_one(
        """
        SELECT b.*, u.username, d.name as destination_display_name
        FROM bookings b
        LEFT JOIN users u ON b.user_id = u.id
        LEFT JOIN destinations d ON b.destination_id = d.id
        WHERE b.id = ?
        """,
        (booking_id,)
    )
    return dict(row) if row else None


def update_booking_status(booking_id: int, status: str) -> bool:
    """Update booking status."""
    try:
        db.execute(
            "UPDATE bookings SET status = ? WHERE id = ?",
            (status, booking_id)
        )
        return True
    except DatabaseError:
        return False


def delete_booking(booking_id: int) -> bool:
    """Delete a booking."""
    try:
        db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        return True
    except DatabaseError:
        return False


# ==================== REVIEW OPERATIONS ====================

def add_review(user_id: int, destination_id: int, rating: int, comment: str = None) -> bool:
    """Add a review for a destination."""
    try:
        db.execute(
            """
            INSERT INTO reviews (user_id, destination_id, rating, comment)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, destination_id, rating, comment)
        )
        
        # Update destination average rating
        update_destination_rating(destination_id)
        return True
    except DatabaseError:
        return False


def update_destination_rating(destination_id: int):
    """Update destination's average rating."""
    result = db.fetch_one(
        "SELECT AVG(rating) as avg_rating FROM reviews WHERE destination_id = ?",
        (destination_id,)
    )
    if result and result['avg_rating']:
        db.execute(
            "UPDATE destinations SET rating = ? WHERE id = ?",
            (round(result['avg_rating'], 1), destination_id)
        )


def get_destination_reviews(destination_id: int) -> List[Dict[str, Any]]:
    """Get all reviews for a destination."""
    rows = db.fetch_all(
        """
        SELECT r.*, u.username, u.full_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.destination_id = ?
        ORDER BY r.created_at DESC
        """,
        (destination_id,)
    )
    return [dict(row) for row in rows]


def get_user_reviews(user_id: int) -> List[Dict[str, Any]]:
    """Get all reviews by a user."""
    rows = db.fetch_all(
        """
        SELECT r.*, d.name as destination_name
        FROM reviews r
        JOIN destinations d ON r.destination_id = d.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        """,
        (user_id,)
    )
    return [dict(row) for row in rows]


# ==================== TRIP PLANNER OPERATIONS ====================

def create_trip_plan(
    user_id: int,
    plan_name: str,
    destination_id: int = None,
    start_date: str = None,
    end_date: str = None,
    budget: float = None,
    notes: str = None
) -> Optional[int]:
    """Create a new trip plan."""
    try:
        plan_id = db.execute_insert(
            """
            INSERT INTO trip_plans (user_id, plan_name, destination_id, start_date, end_date, budget, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, plan_name, destination_id, start_date, end_date, budget, notes)
        )
        return plan_id
    except DatabaseError:
        return None


def get_user_trip_plans(user_id: int) -> List[Dict[str, Any]]:
    """Get all trip plans for a user."""
    rows = db.fetch_all(
        """
        SELECT t.*, d.name as destination_name
        FROM trip_plans t
        LEFT JOIN destinations d ON t.destination_id = d.id
        WHERE t.user_id = ?
        ORDER BY t.created_at DESC
        """,
        (user_id,)
    )
    return [dict(row) for row in rows]


def update_trip_plan(plan_id: int, **kwargs) -> bool:
    """Update trip plan."""
    allowed_fields = ['plan_name', 'destination_id', 'start_date', 'end_date', 'budget', 'notes']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [plan_id]
    
    try:
        db.execute(f"UPDATE trip_plans SET {set_clause} WHERE id = ?", tuple(values))
        return True
    except DatabaseError:
        return False


def delete_trip_plan(plan_id: int) -> bool:
    """Delete a trip plan."""
    try:
        db.execute("DELETE FROM trip_plans WHERE id = ?", (plan_id,))
        return True
    except DatabaseError:
        return False


# ==================== RECOMMENDATION SYSTEM ====================

def get_recommendations(
    user_id: int = None,
    budget: float = None,
    category: str = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Get travel recommendations based on criteria."""
    
    if user_id:
        # Get user preferences
        prefs = db.fetch_one(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        
        if prefs:
            if not category and prefs['preferred_category']:
                category = prefs['preferred_category']
            if not budget and prefs['budget_range_max']:
                budget = prefs['budget_range_max']
    
    # Build query
    sql = "SELECT * FROM destinations WHERE is_active = 1"
    params = []
    
    if budget:
        sql += " AND base_price <= ?"
        params.append(budget)
    
    if category:
        sql += " AND category = ?"
        params.append(category)
    
    # Order by rating and popularity
    sql += " ORDER BY rating DESC, base_price ASC LIMIT ?"
    params.append(limit)
    
    rows = db.fetch_all(sql, tuple(params))
    return [dict(row) for row in rows]


def get_popular_destinations(limit: int = 5) -> List[Dict[str, Any]]:
    """Get most popular destinations based on bookings."""
    rows = db.fetch_all(
        """
        SELECT d.*, COUNT(b.id) as booking_count
        FROM destinations d
        LEFT JOIN bookings b ON d.id = b.destination_id
        WHERE d.is_active = 1
        GROUP BY d.id
        ORDER BY booking_count DESC, d.rating DESC
        LIMIT ?
        """,
        (limit,)
    )
    return [dict(row) for row in rows]


def save_user_preferences(
    user_id: int,
    preferred_category: str = None,
    budget_range_min: float = None,
    budget_range_max: float = None,
    preferred_destinations: str = None
) -> bool:
    """Save or update user preferences."""
    try:
        existing = db.fetch_one(
            "SELECT id FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        
        if existing:
            db.execute(
                """
                UPDATE user_preferences
                SET preferred_category = ?, budget_range_min = ?,
                    budget_range_max = ?, preferred_destinations = ?
                WHERE user_id = ?
                """,
                (preferred_category, budget_range_min, budget_range_max,
                 preferred_destinations, user_id)
            )
        else:
            db.execute(
                """
                INSERT INTO user_preferences
                (user_id, preferred_category, budget_range_min, budget_range_max, preferred_destinations)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, preferred_category, budget_range_min, budget_range_max, preferred_destinations)
            )
        return True
    except DatabaseError:
        return False


# ==================== EXPORT/IMPORT OPERATIONS ====================

def export_user_data(user_id: int) -> Dict[str, Any]:
    """Export all user data for backup."""
    user = get_user_by_id(user_id)
    if not user:
        return {}
    
    return {
        "user_info": user,
        "bookings": get_user_bookings(user_id),
        "trip_plans": get_user_trip_plans(user_id),
        "reviews": get_user_reviews(user_id),
        "exported_at": datetime.now().isoformat()
    }


def calculate_package_price(base_price: float, package_type: str, people: int = 1) -> float:
    """Calculate total price based on package type."""
    multipliers = {
        "Silver": 1.0,
        "Golden": 1.5,
        "Diamond": 2.0
    }
    multiplier = multipliers.get(package_type, 1.0)
    return base_price * multiplier * people
