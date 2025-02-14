import sqlite3
import json

from datetime import datetime
from polymarket_predictions_tally.database import insert_question, load_sql_query
from polymarket_predictions_tally.logic import Question
from polymarket_predictions_tally.utils import assert_fails, parse_datetime


def test_insert_question():
    with sqlite3.connect(":memory:") as conn:

        # Create the questions table (schema must match your actual database)
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Create a test question
        test_question = Question(
            id=10,
            question="Will it rain tomorrow?",
            tag="weather",
            end_date=datetime(2025, 2, 14),
            description="Forecast for tomorrow",
            outcome=None,
            outcome_probs=[0.7, 0.3],
            outcomes=["Yes", "No"],
        )

        # Run the function
        insert_question(conn, test_question)

        # Verify insertion
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM questions WHERE question = ?", (test_question.question,)
        )
        result = cursor.fetchone()

        print(result)

        assert result is not None  # Ensure something was inserted
        assert result[0] == 10
        assert result[1] == "Will it rain tomorrow?"  # Check question text
        assert result[2] == "weather"
        assert parse_datetime(result[3]) == datetime(2025, 2, 14)
        assert result[4] == "Forecast for tomorrow"
        assert result[5] == None
        assert json.loads(result[6]) == [0.7, 0.3]  # Ensure probabilities match
        assert json.loads(result[7]) == ["Yes", "No"]  # Ensure outcomes match


def test_insert_question_optional_fields():
    """
    Test inserting a question with empty JSON fields to verify defaults.
    """
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Create a test question with empty outcome_probs and outcomes
        test_question = Question(
            id=11,
            question="Will it be sunny?",
            tag="weather",
            end_date=datetime(2025, 3, 1),
            description="Sunny forecast",
            outcome=None,
            outcome_probs=[],  # Empty list
            outcomes=[],  # Empty list
        )

        insert_question(conn, test_question)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (11,))
        result = cursor.fetchone()

        assert result is not None
        # Check that empty lists are stored as JSON "[]"
        assert json.loads(result[6]) == []
        assert json.loads(result[7]) == []


def test_multiple_inserts():
    """
    Test inserting multiple questions to ensure each is handled independently.
    """
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        q1 = Question(
            id=1,
            question="Will it snow tomorrow?",
            tag="weather",
            end_date=datetime(2025, 12, 25),
            description="Snow forecast",
            outcome=None,
            outcome_probs=[0.3, 0.7],
            outcomes=["Yes", "No"],
        )

        q2 = Question(
            id=2,
            question="Will it be windy tomorrow?",
            tag="weather",
            end_date=datetime(2025, 6, 1),
            description="Wind forecast",
            outcome=None,
            outcome_probs=[0.6, 0.4],
            outcomes=["Yes", "No"],
        )

        insert_question(conn, q1)
        insert_question(conn, q2)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        assert count == 2


def test_duplicate_id_insertion_fails():
    with sqlite3.connect(":memory:") as conn:
        # Set up the database schema
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Insert the first question with id=1
        q1 = Question(
            id=1,
            question="Is it sunny today?",
            tag="weather",
            end_date=datetime(2025, 1, 1),
            description="Sunny forecast",
            outcome=None,
            outcome_probs=[0.8, 0.2],
            outcomes=["Yes", "No"],
        )
        insert_question(conn, q1)

        # Create a second question with the same id
        q_duplicate = Question(
            id=1,  # Duplicate id
            question="Will it rain today?",
            tag="weather",
            end_date=datetime(2025, 1, 2),
            description="Rain forecast",
            outcome=None,
            outcome_probs=[0.4, 0.6],
            outcomes=["Yes", "No"],
        )

        # Assert that inserting the duplicate question raises an IntegrityError
        assert_fails(insert_question, conn, q_duplicate)
