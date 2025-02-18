from datetime import datetime
import sqlite3
from polymarket_predictions_tally.database.read import get_active_question_ids
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_question
from polymarket_predictions_tally.logic import Question


def test_get_active_question_ids_empty():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # No rows inserted; should return an empty list.
        result = get_active_question_ids(conn)
        assert result == []


def test_get_active_question_ids_non_null_outcomes():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        q1 = Question(
            id=1,
            question="question?",
            tag="general",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            outcome=True,
            end_date=datetime(2025, 1, 1),
            description="description",
        )
        q2 = Question(
            id=2,
            question="question2?",
            tag="general",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            outcome=True,
            end_date=datetime(2025, 1, 1),
            description="description",
        )
        insert_question(conn, q1)
        insert_question(conn, q2)
        result = get_active_question_ids(conn)
        assert result == []


def test_get_active_question_ids_mixed():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        # Insert a mix of questions: outcome = NULL means active.
        q1 = Question(
            id=1,
            question="question?",
            tag="general",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="description",
        )
        q2 = Question(
            id=2,
            question="question2?",
            tag="general",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            outcome=True,
            end_date=datetime(2025, 1, 1),
            description="description",
        )
        q3 = Question(
            id=3,
            question="question3?",
            tag="general",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="description",
        )
        q4 = Question(
            id=4,
            question="question4?",
            tag="general",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            outcome=True,
            end_date=datetime(2025, 1, 1),
            description="description",
        )
        insert_question(conn, q1)  # Active
        insert_question(conn, q2)  # Not active
        insert_question(conn, q3)  # Active
        insert_question(conn, q4)  # Not active
        result = get_active_question_ids(conn)
        # We expect questions 1 and 3 to be active.
        assert set(result) == {1, 3}
