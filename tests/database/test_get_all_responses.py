from datetime import datetime
import sqlite3

from polymarket_predictions_tally.database.read import get_all_responses
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.logic import Question, Response
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user_by_name,
)


def test_get_all_responses_empty():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        # No responses inserted for user 1
        responses = get_all_responses(conn, 1)
        assert responses == []


def test_get_all_responses_returns_responses():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        # Insert two responses for user 1
        insert_user_by_name(conn, "u1")

        q1 = Question(
            id=101,
            question="Question 1",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Desc for Q1",
        )
        q2 = Question(
            id=102,
            question="Question 2",
            outcome_probs=[0.6, 0.4],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 1, 2),
            description="Desc for Q2",
        )
        insert_question(conn, q1)
        insert_question(conn, q2)
        r1 = Response(
            user_id=1,
            question_id=101,
            answer="Yes",
            timestamp=datetime.now(),
            correct=True,
            explanation=None,
        )
        r2 = Response(
            user_id=1,
            question_id=102,
            answer="No",
            timestamp=datetime.now(),
            correct=False,
            explanation="Because",
        )
        insert_response(conn, r1)
        insert_response(conn, r2)
        responses = get_all_responses(conn, 1)
        assert len(responses) == 2
        answers = [resp.answer for resp in responses]
        assert "Yes" in answers
        assert "No" in answers
