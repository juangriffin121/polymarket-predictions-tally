from datetime import datetime
import sqlite3

from polymarket_predictions_tally.database.read import get_latest_responses
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user_by_name,
)
from polymarket_predictions_tally.logic import Question, Response


def test_get_latest_responses_empty():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        # No responses inserted for user_id 1
        responses = get_latest_responses(conn, 1)
        assert responses == []


def test_get_latest_responses_returns_responses():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        # Insert two responses for user_id 1

        insert_user_by_name(conn, "u1")

        q1 = Question(
            id=1,
            question="Question 1",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Desc for Q1",
        )
        q2 = Question(
            id=2,
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
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=True,
            explanation="Explanation to 1",
        )
        r2 = Response(
            user_id=1,
            question_id=2,
            answer="No",
            timestamp=datetime.now(),
            correct=False,
            explanation="Because",
        )

        r2l = Response(
            user_id=1,
            question_id=2,
            answer="Yes",
            timestamp=datetime.now(),
            correct=False,
            explanation="I changed my mind",
        )
        insert_response(conn, r1)
        insert_response(conn, r2)
        insert_response(conn, r2l)
        responses = get_latest_responses(conn, 1)
        assert len(responses) == 2
        explanations = [resp.explanation for resp in responses]
        assert "Explanation to 1" in explanations
        assert "I changed my mind" in explanations
