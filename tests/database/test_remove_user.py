import sqlite3

from polymarket_predictions_tally.database.write import insert_user, remove_user
from polymarket_predictions_tally.logic import User
from polymarket_predictions_tally.utils import load_sql_query


def test_remove_existing_user():
    """Test that a user is removed if they exist."""
    with sqlite3.connect(":memory:") as conn:
        # Set up the schema
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Insert a test user
        test_user = User(id=1, username="Alice", budget=1000)
        insert_user(conn, test_user)

        # Remove the user
        remove_user(conn, test_user.id)

        # Verify the user no longer exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (test_user.id,))
        result = cursor.fetchone()
        assert result is None


def test_remove_nonexistent_user():
    """Test that removing a non-existent user does not cause an error."""
    with sqlite3.connect(":memory:") as conn:
        # Set up the schema
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Attempt to remove a user that doesn't exist (id=999)
        # Depending on your implementation, this may simply do nothing.
        remove_user(conn, 999)

        # Verify that no rows exist (or that the table remains unchanged)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        # In a new database, this should be an empty list.
        assert results == []


def test_remove_user_among_multiple_users():
    """Test that removing one user does not affect the others."""
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Insert multiple users
        user1 = User(id=1, username="Alice", budget=1000)
        user2 = User(id=2, username="Bob", budget=1500)
        user3 = User(id=3, username="Charlie", budget=2000)
        insert_user(conn, user1)
        insert_user(conn, user2)
        insert_user(conn, user3)

        # Remove user with id=2 (Bob)
        remove_user(conn, 2)

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users")
        results = cursor.fetchall()

        # Expect only user1 and user3 remain
        remaining_ids = {row[0] for row in results}
        assert remaining_ids == {1, 3}
        assert len(remaining_ids) == 2
