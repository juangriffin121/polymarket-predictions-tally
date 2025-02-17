import sqlite3

from polymarket_predictions_tally.database import (
    get_user,
    insert_user_by_name,
    load_sql_query,
)
from polymarket_predictions_tally.logic import User
from polymarket_predictions_tally.utils import assert_fails


def test_insert_user_by_name():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        insert_user_by_name(
            conn,
            username="JohnDoe",
        )
        test_user = get_user(conn, "JohnDoe")
        assert test_user is not None

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (test_user.id,))

        result = cursor.fetchone()
        assert result[1] == "JohnDoe"


def test_insert_user_by_name_duplicate_id():
    """Test that inserting a user with a duplicate id raises an error."""
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        insert_user_by_name(
            conn,
            username="JohnDoe",
        )

        assert_fails(
            insert_user_by_name,
            conn,
            username="JohnDoe",
        )


def test_insert_multiple_users():
    """Test that multiple users can be inserted and coexist in the database."""
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        insert_user_by_name(
            conn,
            username="Alice",
        )
        insert_user_by_name(
            conn,
            username="Bob",
        )

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        assert count == 2
