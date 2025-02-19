from datetime import datetime
import sqlite3


from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user,
    update_users_stats,
)
from polymarket_predictions_tally.logic import Question, Response, User


def test_update_users_stats():
    with sqlite3.connect(":memory:") as conn:
        # Setup DB
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Create test data
        u1 = User(id=1, username="u1", budget=100)
        u2 = User(id=2, username="u2", budget=100)
        u3 = User(id=3, username="u3", budget=100)
        insert_user(conn, u1)
        insert_user(conn, u2)
        insert_user(conn, u3)

        q1 = Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Weather",
            outcome=True,
            end_date=datetime.now(),
            description="Test question.",
        )

        q2 = Question(
            id=2,
            question="Will it rain next Monday?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Weather",
            outcome=False,
            end_date=datetime.now(),
            description="Test question.",
        )

        insert_question(conn, q1)
        insert_question(conn, q2)

        ru1q1 = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=True,
            explanation=None,
        )

        ru1q2 = Response(
            user_id=1,
            question_id=2,
            answer="Yes",
            timestamp=datetime.now(),
            correct=False,
            explanation=None,
        )

        ru2q1 = Response(
            user_id=2,
            question_id=1,
            answer="No",
            timestamp=datetime.now(),
            correct=True,
            explanation=None,
        )

        insert_response(conn, ru1q1)
        insert_response(conn, ru1q2)
        insert_response(conn, ru2q1)

        # Prepare update_info
        update_info = {u1: [(ru1q1, True), (ru1q2, False)], u2: [(ru2q1, True)]}

        # Call function
        update_users_stats(conn, update_info)

        # Assertions
        cursor = conn.cursor()
        cursor.execute(
            "SELECT correct_answers, incorrect_answers FROM stats WHERE user_id = ?",
            (u1.id,),
        )
        stats = cursor.fetchone()

        assert stats is not None
        assert stats[0] == 1  # correct_answers
        assert stats[1] == 1  # incorrect_answers

        cursor.execute(
            "SELECT correct_answers, incorrect_answers FROM stats WHERE user_id = ?",
            (u2.id,),
        )

        stats = cursor.fetchone()

        assert stats is not None
        assert stats[0] == 1  # correct_answers
        assert stats[1] == 0  # incorrect_answers

        cursor.execute(
            "SELECT correct_answers, incorrect_answers FROM stats WHERE user_id = ?",
            (u3.id,),
        )

        stats = cursor.fetchone()

        assert stats is not None
        assert stats[0] == 0  # correct_answers
        assert stats[1] == 0  # incorrect_answers
