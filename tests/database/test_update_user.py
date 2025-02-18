import sqlite3

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_user, update_user
from polymarket_predictions_tally.logic import User
from polymarket_predictions_tally.utils import assert_fails


def test_update_existing_user():
    """Test that updating an existing user's budget works as expected."""
    with sqlite3.connect(":memory:") as conn:
        # Set up the schema
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Insert a test user
        user = User(id=1, username="Alice", budget=1000)
        insert_user(conn, user)

        # Update the user's budget
        update_user(conn, id=1, new_budget=1500)

        # Verify that the budget has been updated
        cursor = conn.cursor()
        cursor.execute("SELECT budget FROM users WHERE id = ?", (1,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 1500


def test_update_nonexistent_user():
    """
    Test that attempting to update a non-existent user does not insert a new record.
    (Assuming update_user only performs an UPDATE and does not upsert.)
    """
    with sqlite3.connect(":memory:") as conn:
        # Set up the schema
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Attempt to update a user that doesn't exist
        assert_fails(update_user, conn, id=999, new_budget=1500)

        # Verify that no user was added (table remains empty)


def test_update_user_among_multiple_users():
    """Test that updating one user does not affect the budgets of others."""
    with sqlite3.connect(":memory:") as conn:
        # Set up the schema
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Insert multiple users
        user1 = User(id=1, username="Alice", budget=1000)
        user2 = User(id=2, username="Bob", budget=2000)
        insert_user(conn, user1)
        insert_user(conn, user2)

        # Update Bob's budget only
        update_user(conn, id=2, new_budget=2500)

        cursor = conn.cursor()
        cursor.execute("SELECT id, budget FROM users")
        rows = cursor.fetchall()
        # Create a dictionary of id to budget for easy checking
        budgets = {row[0]: row[1] for row in rows}

        assert budgets[1] == 1000  # Alice remains unchanged
        assert budgets[2] == 2500  # Bob's budget updated
