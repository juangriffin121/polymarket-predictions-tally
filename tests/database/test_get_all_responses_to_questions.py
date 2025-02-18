import sqlite3
from datetime import datetime

from polymarket_predictions_tally.database.read import get_all_responses_to_questions
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user_by_name,
)
from polymarket_predictions_tally.logic import Question, Response, User


# --- Helper to create the test database schema ---
def create_questions_table(conn: sqlite3.Connection):
    start_db = load_sql_query("./database/setup.sql")
    conn.executescript(start_db)


# --- Test when no responses have been inserted ---
def test_get_all_responses_empty():
    with sqlite3.connect(":memory:") as conn:
        create_questions_table(conn)
        # Create two questions with no responses.
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

        responses = get_all_responses_to_questions(conn, [q1, q2])
        # Expect a list with two elements, each an empty list.
        assert isinstance(responses, list)
        assert len(responses) == 2
        assert responses[0] == []
        assert responses[1] == []


# --- Test when responses exist for each question ---
def test_get_all_responses_returns_correct_responses():
    with sqlite3.connect(":memory:") as conn:
        create_questions_table(conn)
        # Create two questions.
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

        # Insert responses for these questions.
        # Two responses for q1.
        insert_user_by_name(conn, "JohnDoe")
        insert_user_by_name(conn, "JaneDoe")
        insert_user_by_name(conn, "DoeDeer")
        r1 = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=True,
            explanation=None,
        )
        r2 = Response(
            user_id=2,
            question_id=1,
            answer="No",
            timestamp=datetime.now(),
            correct=False,
            explanation="Because",
        )
        # One response for q2.
        r3 = Response(
            user_id=3,
            question_id=2,
            answer="Yes",
            timestamp=datetime.now(),
            correct=True,
            explanation="Sure",
        )
        insert_response(conn, r1)
        insert_response(conn, r2)
        insert_response(conn, r3)

        responses = get_all_responses_to_questions(conn, [q1, q2])
        # Expect two lists: first with two responses, second with one.
        assert isinstance(responses, list)
        assert len(responses) == 2
        assert len(responses[0]) == 2  # Responses for q1
        assert len(responses[1]) == 1  # Responses for q2

        # Validate that each response is for the correct question.
        for resp in responses[0]:
            assert resp.question_id == 1
        for resp in responses[1]:
            assert resp.question_id == 2
