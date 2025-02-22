import sqlite3

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_user
from polymarket_predictions_tally.logic import User
from polymarket_predictions_tally.utils import assert_fails


def test_insert_user():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        test_user = User(
            id=5,
            username="JohnDoe",
            budget=1000,
        )
        insert_user(conn, test_user)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (test_user.id,))

        result = cursor.fetchone()
        assert list(result) == [v for v in test_user.__dict__.values()]


def test_insert_user_duplicate_id():
    """Test that inserting a user with a duplicate id raises an error."""
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        user1 = User(
            id=5,
            username="JohnDoe",
            budget=1000,
        )
        insert_user(conn, user1)

        duplicate_user = User(
            id=5,  # Same id as user1
            username="JaneDoe",
            budget=500,
        )
        assert_fails(insert_user, conn, duplicate_user)


def test_insert_multiple_users():
    """Test that multiple users can be inserted and coexist in the database."""
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        user1 = User(
            id=1,
            username="Alice",
            budget=2000,
        )
        user2 = User(
            id=2,
            username="Bob",
            budget=1500,
        )
        insert_user(conn, user1)
        insert_user(conn, user2)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        assert count == 2
