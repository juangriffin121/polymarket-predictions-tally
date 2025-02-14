from datetime import datetime
import json
import sqlite3

from polymarket_predictions_tally.database import (
    insert_question,
    load_sql_query,
    remove_question,
)
from polymarket_predictions_tally.logic import Question
from polymarket_predictions_tally.utils import assert_fails


def test_remove_question():
    with sqlite3.connect(":memory:") as conn:
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

        # Insert the question
        insert_question(conn, test_question)
        remove_question(conn, test_question.id)

        cursor = conn.cursor()
        cursor.execute("SELECT * from questions")
        result = cursor.fetchone()
        assert result == None


def test_remove_non_existent_question():
    with sqlite3.connect(":memory:") as conn:
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

        # Insert the question
        insert_question(conn, test_question)
        assert_fails(remove_question, conn, 5)
