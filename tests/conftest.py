import os
import tempfile
import pytest
import database

REAL_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "database", "travel.db")
)


@pytest.fixture(autouse=True)
def isolate_database():
    """Ensure every test runs against an isolated temporary database, never the real one."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = f.name

    # Point database module to temporary file
    database.set_database_path(temp_db_path)

    # Guard against targeting the production database
    current_resolved = os.path.abspath(database.db.db_path)
    is_real_db = False
    if os.path.exists(REAL_DB_PATH) and os.path.exists(current_resolved):
        try:
            is_real_db = os.path.samefile(current_resolved, REAL_DB_PATH)
        except OSError:
            is_real_db = current_resolved == REAL_DB_PATH
    else:
        is_real_db = current_resolved == REAL_DB_PATH

    if is_real_db:
        database.set_database_path(None)
        raise RuntimeError(
            f"GUARD FAILED: Test attempted to access production database: {current_resolved}"
        )

    # Initialize schema and sample destinations in temp database
    database.init_database()

    yield temp_db_path

    # Teardown: reset path and remove temp database
    database.set_database_path(None)
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except OSError:
            pass
