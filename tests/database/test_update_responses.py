import sqlite3
import pytest
from datetime import datetime

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user_by_name,
    update_responses,
)
from polymarket_predictions_tally.logic import Question, Response


def test_update_responses_updates_correct_flag():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        # Create a question that has an outcome.
        # For example, outcome=True corresponds to "Yes".
        question = Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.7, 0.3],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=True,
            end_date=datetime(2025, 1, 1),
            description="Initial description",
        )
        insert_question(conn, question)

        # Insert two responses for question 1:
        # r1 with answer "Yes" should become correct True,
        # r2 with answer "No" should become correct False.
        insert_user_by_name(conn, "JohnDoe")
        insert_user_by_name(conn, "JaneDoe")
        r1 = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        r2 = Response(
            user_id=2,
            question_id=1,
            answer="No",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        insert_response(conn, r1)
        insert_response(conn, r2)

        # Group responses as a list of lists, one per question.
        responses_group = [[r1, r2]]
        # Call update_responses which should update the 'correct' column.
        update_responses(conn, responses_group, [question])

        # Verify that the responses in the DB were updated:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT answer, correct FROM responses WHERE question_id = ?", (1,)
        )
        rows = cursor.fetchall()
        # We expect that a response with answer "Yes" is marked correct (True) and with "No" is marked incorrect (False).
        for answer, correct in rows:
            if answer == "Yes":
                assert correct in (1, True)
            elif answer == "No":
                assert correct in (0, False)
            else:
                pytest.fail("Unexpected answer value in DB")


def test_update_responses_does_nothing_when_outcome_none():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        # Create a question with outcome set to None.
        question = Question(
            id=2,
            question="Will it snow tomorrow?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 1, 2),
            description="Initial description",
        )
        insert_question(conn, question)
        insert_user_by_name(conn, "JohnDoe")
        insert_user_by_name(conn, "JaneDoe")

        # Insert two responses for question 2.
        r3 = Response(
            user_id=1,
            question_id=2,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        r4 = Response(
            user_id=2,
            question_id=2,
            answer="No",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        insert_response(conn, r3)
        insert_response(conn, r4)

        responses_group = [[r3, r4]]
        # Since the outcome is None, update_responses should not modify the responses.
        update_responses(conn, responses_group, [question])

        cursor = conn.cursor()
        cursor.execute(
            "SELECT answer, correct FROM responses WHERE question_id = ?", (2,)
        )
        rows = cursor.fetchall()
        # Both responses should have 'correct' still set to None.
        for answer, correct in rows:
            assert correct is None
