import sqlite3
import json
from datetime import datetime
from typing import assert_never

from polymarket_predictions_tally.database import (
    insert_question,
    load_sql_query,
    update_question,
)
from polymarket_predictions_tally.logic import Question
from polymarket_predictions_tally.utils import assert_fails


def test_update_existing_question_success():
    """Test that updating an existing question correctly changes all fields."""
    with sqlite3.connect(":memory:") as conn:
        # Set up the schema
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Insert an initial question
        original_question = Question(
            id=1,
            question="Original question?",
            tag="general",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Original description",
        )
        insert_question(conn, original_question)

        # Update the question with new values
        updated_question = Question(
            id=1,
            question="Updated question?",
            tag="updated_tag",
            outcome_probs=[0.7, 0.3],
            outcomes=["Maybe", "Definitely"],
            outcome=True,
            end_date=datetime(2025, 2, 2),
            description="Updated description",
        )
        update_question(conn, updated_question)

        # Query the updated row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (1,))
        result = cursor.fetchone()
        print(result)

        # Expected column order:
        # (id, question, tag, end_date, description, resolved, outcome, outcome_probs, outcomes)
        assert result is not None
        assert result[0] == 1
        assert result[1] == "Updated question?"
        assert result[2] == "updated_tag"
        # Convert the stored datetime string into a datetime object for comparison
        assert datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S") == datetime(2025, 2, 2)
        assert result[4] == "Updated description"
        assert result[5]
        assert json.loads(result[6]) == [0.7, 0.3]
        assert json.loads(result[7]) == ["Maybe", "Definitely"]


def test_update_nonexistent_question():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        non_existent_question = Question(
            id=99,
            question="Non-existent question?",
            tag="none",
            outcome_probs=[0.1, 0.9],
            outcomes=["No", "Yes"],
            outcome=None,
            end_date=datetime(2025, 12, 31),
            description="This question does not exist",
        )
        assert_fails(update_question, conn, non_existent_question)


def test_multiple_updates():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("./database/setup.sql")
        conn.executescript(start_db)

        # Insert two questions
        question1 = Question(
            id=1,
            question="Question one?",
            tag="tag1",
            outcome_probs=[0.2, 0.8],
            outcomes=["A", "B"],
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="First question",
        )
        question2 = Question(
            id=2,
            question="Question two?",
            tag="tag2",
            outcome_probs=[0.3, 0.7],
            outcomes=["C", "D"],
            outcome=False,
            end_date=datetime(2025, 1, 2),
            description="Second question",
        )
        insert_question(conn, question1)
        insert_question(conn, question2)

        # Update only question1
        updated_question1 = Question(
            id=1,
            question="Updated question one?",
            tag="updated_tag1",
            outcome_probs=[0.9, 0.1],
            outcomes=["X", "Y"],
            outcome=True,
            end_date=datetime(2025, 1, 10),
            description="Updated first question",
        )
        update_question(conn, updated_question1)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (1,))
        result1 = cursor.fetchone()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (2,))
        result2 = cursor.fetchone()

        # Verify that question1 is updated
        assert result1 is not None
        assert result1[1] == "Updated question one?"
        assert result1[2] == "updated_tag1"
        assert datetime.strptime(result1[3], "%Y-%m-%d %H:%M:%S") == datetime(
            2025, 1, 10
        )
        assert result1[4] == "Updated first question"
        assert result1[5]
        assert json.loads(result1[6]) == [0.9, 0.1]
        assert json.loads(result1[7]) == ["X", "Y"]

        # Verify that question2 remains unchanged
        assert result2 is not None
        assert result2[1] == "Question two?"
        assert result2[2] == "tag2"
        assert datetime.strptime(result2[3], "%Y-%m-%d %H:%M:%S") == datetime(
            2025, 1, 2
        )
        assert result2[4] == "Second question"
        assert not result2[5]
        assert json.loads(result2[6]) == [0.3, 0.7]
        assert json.loads(result2[7]) == ["C", "D"]
