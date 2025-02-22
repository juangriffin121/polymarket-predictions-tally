import sqlite3
from datetime import datetime
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    update_questions,
)
from polymarket_predictions_tally.logic import Question


# Helper function to create the test database schema
def create_questions_table(conn: sqlite3.Connection):
    start_db = load_sql_query("setup.sql")
    conn.executescript(start_db)


def test_update_questions_updates_existing_question():
    with sqlite3.connect(":memory:") as conn:
        create_questions_table(conn)
        # Insert an initial question.
        initial_question = Question(
            id=1,
            question="Initial question",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Initial description",
        )
        insert_question(conn, initial_question)

        # Create an updated version of the question.
        updated_question = Question(
            id=1,  # Same id, so it should update the existing row.
            question="Updated question",
            outcome_probs=[0.7, 0.3],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=True,  # Changed outcome from None to True.
            end_date=datetime(2025, 1, 1),
            description="Updated description",
        )
        update_questions(conn, [updated_question])

        # Query the updated row.
        cursor = conn.cursor()
        cursor.execute(
            "SELECT question, outcome, description FROM questions WHERE id = ?", (1,)
        )
        row = cursor.fetchone()

        # Assert that the values were updated.
        assert row is not None
        assert row[0] == "Updated question"
        # SQLite stores booleans as integers, so True should be 1.
        assert row[1] == 1
        assert row[2] == "Updated description"


def test_update_questions_skips_none():
    with sqlite3.connect(":memory:") as conn:
        create_questions_table(conn)
        # Insert an initial question.
        initial_question = Question(
            id=1,
            question="Initial question",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Initial description",
        )
        insert_question(conn, initial_question)

        # Call update_questions with a list that contains a None.
        update_questions(conn, [None])

        # Query the database to ensure nothing was updated.
        cursor = conn.cursor()
        cursor.execute(
            "SELECT question, outcome, description FROM questions WHERE id = ?", (1,)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "Initial question"
        # Outcome remains NULL (None in Python).
        assert row[1] is None
        assert row[2] == "Initial description"
