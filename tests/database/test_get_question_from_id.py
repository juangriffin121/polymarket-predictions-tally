from datetime import datetime
import sqlite3
import pytest
from polymarket_predictions_tally.database.read import get_question_from_id
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_question
from polymarket_predictions_tally.logic import Question


def test_get_question_from_id_exists():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        q = Question(
            id=1,
            question="Test question",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Test",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Test description",
        )
        insert_question(conn, q)
        fetched = get_question_from_id(conn, 1)
        assert fetched is not None
        assert fetched.question == "Test question"
        assert fetched.tag == "Test"


def test_get_question_from_id_not_found():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)
        # With no question inserted, calling get_question_from_id should result in a TypeError
        # because fetchone() will return None and then results[0] will fail.
        with pytest.raises(TypeError):
            get_question_from_id(conn, 999)
