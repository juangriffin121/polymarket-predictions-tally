import sqlite3

from polymarket_predictions_tally.database.read import get_all_users
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_user
from polymarket_predictions_tally.logic import User


def test_get_all_users_empty():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        users = get_all_users(conn)
        assert users == []


def test_get_all_users_returns_users():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        user1 = User(id=1, username="Alice", budget=100)
        user2 = User(id=2, username="Bob", budget=150)
        insert_user(conn, user1)
        insert_user(conn, user2)
        users = get_all_users(conn)
        assert len(users) == 2
        usernames = {user.username for user in users}
        assert usernames == {"Alice", "Bob"}
