import sqlite3
from datetime import datetime

from polymarket_predictions_tally.database.read import get_users_affected_by_update
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user_by_name,
)
from polymarket_predictions_tally.logic import Question, Response, User


def test_get_users_affected_by_update_single_question():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        # Insert users (assume insert_user is available; if not, manually insert rows)
        alice = User(id=1, username="Alice", budget=100)
        bob = User(id=2, username="Bob", budget=150)
        charlie = User(id=3, username="Charlie", budget=150)
        # For testing, you can insert users with a simple INSERT if you have no helper:
        conn.execute(
            "INSERT INTO users (id, username, budget) VALUES (?, ?, ?)",
            (alice.id, alice.username, alice.budget),
        )
        conn.execute(
            "INSERT INTO users (id, username, budget) VALUES (?, ?, ?)",
            (bob.id, bob.username, bob.budget),
        )
        conn.execute(
            "INSERT INTO users (id, username, budget) VALUES (?, ?, ?)",
            (charlie.id, charlie.username, charlie.budget),
        )
        conn.commit()

        # Create a question with a known outcome (e.g. "Yes")
        question = Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.7, 0.3],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=True,
            end_date=datetime(2025, 2, 20),
            description="Forecast Q1",
        )
        insert_question(conn, question)

        # Create responses for this question.
        # Alice answered "Yes" (correct) and Bob answered "No" (incorrect)
        response_alice = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        response_bob = Response(
            user_id=2,
            question_id=1,
            answer="No",
            timestamp=datetime.now(),
            correct=None,
            explanation=None,
        )
        insert_response(conn, response_alice)
        insert_response(conn, response_bob)

        # Construct latest_responses: a list (one element per question) of dictionaries keyed by user_id.
        latest_responses = [{1: response_alice, 2: response_bob}]
        updated_questions = [question]

        result = get_users_affected_by_update(conn, latest_responses, updated_questions)

        # Expect result to be a dict mapping each User to a list of one (Response, bool) tuple.
        # For Alice, the tuple should be (response_alice, True); for Bob, (response_bob, False)
        assert isinstance(result, dict)
        # Check for Alice and Bob by matching their usernames.
        found_alice = False
        found_bob = False
        found_charlie = False
        for user, tup_list in result.items():
            if user.username == "Alice":
                found_alice = True
                assert len(tup_list) == 1
                resp, is_correct = tup_list[0]
                assert resp.user_id == 1
                assert is_correct is True
            elif user.username == "Bob":
                found_bob = True
                assert len(tup_list) == 1
                resp, is_correct = tup_list[0]
                assert resp.user_id == 2
                assert is_correct is False
            elif user.username == "Charlie":
                found_charlie = True
        assert found_alice and found_bob and not found_charlie


def test_get_users_affected_by_update_multiple_questions():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        # Insert two users: Alice and Bob.
        alice = User(id=1, username="Alice", budget=100)
        bob = User(id=2, username="Bob", budget=150)
        conn.execute(
            "INSERT INTO users (id, username, budget) VALUES (?, ?, ?)",
            (alice.id, alice.username, alice.budget),
        )
        conn.execute(
            "INSERT INTO users (id, username, budget) VALUES (?, ?, ?)",
            (bob.id, bob.username, bob.budget),
        )
        conn.commit()

        # Create two questions:
        # Q1 outcome "Yes", Q2 outcome "No"
        question1 = Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.7, 0.3],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=True,
            end_date=datetime(2025, 2, 20),
            description="Forecast Q1",
        )
        question2 = Question(
            id=2,
            question="Will it snow tomorrow?",
            outcome_probs=[0.4, 0.6],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=False,
            end_date=datetime(2025, 2, 21),
            description="Forecast Q2",
        )
        insert_question(conn, question1)
        insert_question(conn, question2)

        # Create responses for Q1:
        # Alice: "Yes" (correct), Bob: "No" (incorrect)
        r1 = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime(2025, 2, 19, 12, 0),
            correct=None,
            explanation=None,
        )
        r2 = Response(
            user_id=2,
            question_id=1,
            answer="No",
            timestamp=datetime(2025, 2, 19, 12, 0),
            correct=None,
            explanation=None,
        )
        # Create responses for Q2:
        # Alice: "Yes" (incorrect), Bob: "No" (correct)
        r3 = Response(
            user_id=1,
            question_id=2,
            answer="Yes",
            timestamp=datetime(2025, 2, 20, 12, 0),
            correct=None,
            explanation=None,
        )
        r4 = Response(
            user_id=2,
            question_id=2,
            answer="No",
            timestamp=datetime(2025, 2, 20, 12, 0),
            correct=None,
            explanation=None,
        )
        insert_response(conn, r1)
        insert_response(conn, r2)
        insert_response(conn, r3)
        insert_response(conn, r4)

        # Build latest_responses for both questions:
        latest_responses = [
            {1: r1, 2: r2},  # For question1
            {1: r3, 2: r4},  # For question2
        ]
        updated_questions = [question1, question2]
        result = get_users_affected_by_update(conn, latest_responses, updated_questions)

        # Expected result:
        # For Alice: Q1 (Yes == Yes -> True), Q2 (Yes != No -> False)
        # For Bob:   Q1 (No != Yes -> False), Q2 (No == No -> True)
        assert isinstance(result, dict)
        for user, data in result.items():
            if user.username == "Alice":
                assert len(data) == 2
                # data is a list of tuples (Response, bool)
                flags = [flag for (_, flag) in data]
                assert flags == [True, False]
            elif user.username == "Bob":
                assert len(data) == 2
                flags = [flag for (_, flag) in data]
                assert flags == [False, True]
