from datetime import datetime
import sqlite3
from polymarket_predictions_tally.database.read import has_user_answered
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user,
)
from polymarket_predictions_tally.logic import InvalidResponse, Question, Response, User
from polymarket_predictions_tally.utils import (
    assert_fails,
    assert_fails_with_exception,
    parse_datetime,
)


def setup_db(conn: sqlite3.Connection):
    start_db = load_sql_query("setup.sql")
    conn.executescript(start_db)

    question = Question(
        id=1,
        question="Will it rain tomorrow?",
        tag="weather",
        end_date=datetime(2025, 2, 14),
        description="Forecast for tomorrow",
        outcome=None,
        outcome_probs=[0.7, 0.3],
        outcomes=["Yes", "No"],
    )

    # Run the function
    insert_question(conn, question)

    user = User(
        id=1,
        username="JohnDoe",
        budget=1000,
    )
    insert_user(conn, user)


def test_insert_valid_response():
    with sqlite3.connect(":memory:") as conn:
        setup_db(conn)
        now = datetime.now()
        response = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=now,
            correct=None,
            explanation=None,
        )
        insert_response(conn, response)

        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM responses WHERE user_id = ? AND question_id = ?",
            (response.user_id, response.question_id),
        )

        result = cursor.fetchone()

        assert result[0] == 1
        assert result[1] == 1
        assert result[2] == 1
        assert result[3] == "Yes"

        assert parse_datetime(result[4]) == now
        assert result[5] == None
        assert result[6] == None


def test_insert_duplicate_response():
    with sqlite3.connect(":memory:") as conn:
        setup_db(conn)

        response = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        insert_response(conn, response)

        response2 = Response(
            user_id=1,
            question_id=1,
            answer="No",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )

        assert_fails(insert_response, conn, response2)


def test_insert_multiple_response():
    with sqlite3.connect(":memory:") as conn:
        setup_db(conn)

        response = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        insert_response(conn, response)

        response2 = Response(
            user_id=1,
            question_id=1,
            answer="Maybe",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        insert_response(conn, response2)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses")
        count = cursor.fetchone()[0]
        assert count == 2


def test_insert_response_invalid_user():
    """
    Test that a response with an invalid user id raises an InvalidResponse.
    """
    with sqlite3.connect(":memory:") as conn:
        setup_db(conn)

        # Create a Response with a user_id that does not exist (999) but with a valid question id (1)
        invalid_response = Response(
            user_id=999,  # Invalid user id
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        assert_fails_with_exception(
            insert_response, conn, invalid_response, expected_exception=InvalidResponse
        )


def test_insert_response_invalid_question():
    """
    Test that a response with an invalid question id raises an InvalidResponse.
    """
    with sqlite3.connect(":memory:") as conn:
        setup_db(conn)

        # Create a Response with a valid user id (1) but an invalid question id (999)
        invalid_response = Response(
            user_id=1,
            question_id=999,  # Invalid question id
            answer="No",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        assert_fails_with_exception(
            insert_response, conn, invalid_response, expected_exception=InvalidResponse
        )


def test_has_user_answered_returns_response():
    """Test that has_user_answered returns a Response when a user has answered the question."""
    with sqlite3.connect(":memory:") as conn:
        setup_db(conn)
        # Insert a response for user id=1 and question id=1.
        response = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=True,
            explanation="Test explanation",
        )
        insert_response(conn, response)

        # Now check that has_user_answered returns a Response.
        result = has_user_answered(conn, 1, 1)
        assert result is not None
        assert result.answer == "Yes"
        assert result.user_id == 1
        assert result.question_id == 1


def test_has_user_answered_returns_none():
    """Test that has_user_answered returns None when no response exists."""
    with sqlite3.connect(":memory:") as conn:
        setup_db(conn)
        # Do not insert any response.
        result = has_user_answered(conn, 1, 1)
        assert result is None
