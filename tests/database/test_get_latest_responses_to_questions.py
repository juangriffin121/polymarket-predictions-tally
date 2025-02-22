import sqlite3
import datetime

from polymarket_predictions_tally.database.read import get_latest_responses_to_questions
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user_by_name,
)
from polymarket_predictions_tally.logic import Question, Response


def test_get_latest_responses_to_questions():
    with sqlite3.connect(":memory:") as conn:
        # Initialize the database
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        # Create test questions
        question1 = Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.6, 0.4],
            outcomes=["Yes", "No"],
            tag="Weather",
            outcome=None,
            end_date=datetime.datetime(2025, 2, 20, 12, 0),
            description="Weather forecast prediction.",
        )
        question2 = Question(
            id=2,
            question="Will the stock market go up?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Finance",
            outcome=None,
            end_date=datetime.datetime(2025, 2, 21, 12, 0),
            description="Stock market prediction.",
        )

        insert_question(conn, question1)
        insert_question(conn, question2)

        # Create test responses with different timestamps
        response1_old = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.datetime(2025, 2, 19, 10, 0),
            correct=None,
            explanation=None,
        )
        response1_latest = Response(
            user_id=1,
            question_id=1,
            answer="No",
            timestamp=datetime.datetime(2025, 2, 19, 15, 0),  # Later timestamp
            correct=None,
            explanation=None,
        )
        response2 = Response(
            user_id=2,
            question_id=2,
            answer="Yes",
            timestamp=datetime.datetime(2025, 2, 20, 14, 0),
            correct=None,
            explanation=None,
        )
        insert_user_by_name(conn, "JohnDoe")
        insert_user_by_name(conn, "JaneDoe")

        # Insert responses into the database
        insert_response(conn, response1_old)
        insert_response(conn, response1_latest)  # Should overwrite old response
        insert_response(conn, response2)

        # Call function
        latest_responses = get_latest_responses_to_questions(
            conn, [question1, question2]
        )

        # Assertions
        assert isinstance(latest_responses, list)
        assert len(latest_responses) == 2  # One entry per question
        assert 1 in latest_responses[0]  # User 1's response to question 1
        assert latest_responses[0][1].answer == "No"  # Latest answer is "No"
        assert 2 in latest_responses[1]  # User 2's response to question 2
        assert latest_responses[1][2].answer == "Yes"  # Their answer is "Yes"
