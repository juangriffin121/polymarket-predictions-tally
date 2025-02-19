import sqlite3

from polymarket_predictions_tally.database.read import get_stats
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_user_by_name,
    update_user_stats,
)


def test_get_stats_initial():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        # Insert a user and create default stats (assumed to initialize both to 0)
        insert_user_by_name(conn, "u1")
        stats = get_stats(conn, 1)
        assert stats == (0, 0)


def test_get_stats_after_update():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        # Insert a user and create default stats
        insert_user_by_name(conn, "u1")
        # Update stats: add 2 correct responses and 3 incorrect responses
        update_user_stats(conn, 1, 2, 3)
        stats = get_stats(conn, 1)
        assert stats == (2, 3)
