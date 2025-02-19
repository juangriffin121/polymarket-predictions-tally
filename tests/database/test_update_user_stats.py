import sqlite3

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_user_by_name,
    update_user_stats,
)


def test_update_user_stats_initial_update():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        # Create a user with default stats.
        insert_user_by_name(conn, username="Alice")

        # Verify initial stats are 0.
        cursor = conn.cursor()
        cursor.execute(
            "SELECT correct_answers, incorrect_answers FROM stats WHERE user_id = ?",
            (1,),
        )
        row = cursor.fetchone()
        assert row is not None, "Stats row must exist for user"
        assert row[0] == 0, "Initial correct_answers should be 0"
        assert row[1] == 0, "Initial incorrect_answers should be 0"

        # Update stats with 2 correct responses and 3 incorrect responses.
        update_user_stats(
            conn, user_id=1, new_correct_responses=2, new_incorrect_responses=3
        )

        # Verify the updated stats.
        cursor.execute(
            "SELECT correct_answers, incorrect_answers FROM stats WHERE user_id = ?",
            (1,),
        )
        row = cursor.fetchone()
        assert row[0] == 2, "Correct answers should be updated to 2"
        assert row[1] == 3, "Incorrect answers should be updated to 3"


def test_update_user_stats_multiple_updates():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        insert_user_by_name(conn, username="Alice")

        # First update.
        update_user_stats(
            conn, user_id=1, new_correct_responses=2, new_incorrect_responses=3
        )
        # Second update.
        update_user_stats(
            conn, user_id=1, new_correct_responses=1, new_incorrect_responses=1
        )

        cursor = conn.cursor()
        cursor.execute(
            "SELECT correct_answers, incorrect_answers FROM stats WHERE user_id = ?",
            (1,),
        )
        row = cursor.fetchone()
        # Expect cumulative totals: 2+1=3 and 3+1=4.
        assert row[0] == 3, "Correct answers should sum to 3"
        assert row[1] == 4, "Incorrect answers should sum to 4"
