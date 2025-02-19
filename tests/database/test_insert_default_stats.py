import sqlite3

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_default_stats,
    insert_user,
    insert_user_by_name,
)
from polymarket_predictions_tally.logic import User


def test_insert_default_stats():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        # Call the function directly.
        insert_default_stats(conn, user_id=1)
        cursor = conn.cursor()
        # Check that a stats row exists for user_id 1.
        cursor.execute("SELECT * FROM stats WHERE user_id = ?", (1,))
        row = cursor.fetchone()
        assert row is not None, "Default stats should be inserted for user_id 1"


def test_insert_user_inserts_default_stats():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        # Create a user.
        user = User(id=1, username="Alice", budget=100)
        insert_user(conn, user)
        cursor = conn.cursor()
        # Verify the user was inserted.
        cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
        user_row = cursor.fetchone()
        assert user_row is not None, "User should be inserted into the users table"
        # Verify that default stats were inserted.
        cursor.execute("SELECT * FROM stats WHERE user_id = ?", (1,))
        stats_row = cursor.fetchone()
        assert stats_row is not None, "Default stats should be inserted for the user"


def test_insert_user_by_name_inserts_default_stats():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        username = "Bob"
        insert_user_by_name(conn, username)
        cursor = conn.cursor()
        # Verify that a user with the given username exists.
        cursor.execute(
            "SELECT id, username, budget FROM users WHERE username = ?", (username,)
        )
        user_row = cursor.fetchone()
        assert user_row is not None, "User should be inserted via insert_user_by_name"
        user_id = user_row[0]
        # Verify that default stats were inserted for that user.
        cursor.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,))
        stats_row = cursor.fetchone()
        assert (
            stats_row is not None
        ), "Default stats should be inserted for the user inserted by name"
