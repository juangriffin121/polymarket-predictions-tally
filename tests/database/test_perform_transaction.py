from datetime import datetime
import sqlite3

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_user, perform_transaction
from polymarket_predictions_tally.logic import Position, Question, Transaction, User


def insert_position(conn: sqlite3.Connection, position: Position):
    cursor = conn.cursor()
    query = """
    INSERT INTO positions (user_id, question_id, stake_yes, stake_no)
    VALUES (?, ?, ?, ?)
    """
    cursor.execute(
        query,
        (position.user_id, position.question_id, position.stake_yes, position.stake_no),
    )
    conn.commit()


def test_perform_transaction_valid():
    with sqlite3.connect(":memory:") as conn:
        # Set up the test database
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        # Insert a user and a corresponding initial position.
        insert_user(conn, User(id=1, username="Alice", budget=1000000))
        # Assume a helper function insert_position exists; if not, perform an INSERT manually.

        # Create a valid transaction: user 1, question 101.
        transaction = Transaction(
            user_id=1,
            question_id=101,
            transaction_type="buy",
            answer=True,  # Let's assume "True" corresponds to buying "Yes" stake.
            amount=100,
        )

        question = Question(
            id=101,
            question="Will Julius Caesar win the 100 BC roman dictatorial election?",
            outcome_probs=[0.9, 0.1],
            outcomes=["Yes", "No"],
            end_date=datetime(100, 10, 10),
            outcome=None,
            description="",
            tag="Politics",
        )

        # Perform the transaction.
        perform_transaction(conn, transaction, None, question)

        # Verify that a transaction record was inserted.
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE user_id = ? AND question_id = ?",
            (1, 101),
        )
        trans_count = cur.fetchone()[0]
        assert trans_count == 1

        # Verify that the positions table was updated.
        # (Assuming get_new_position logic: for a "buy" on True, stake_yes increases by amount,
        # and budget_delta equals -amount)
        cur.execute(
            "SELECT stake_yes, stake_no FROM positions WHERE user_id = ? AND question_id = ?",
            (1, 101),
        )
        pos = cur.fetchone()
        assert pos is not None
        expected_stake_yes = 0 + transaction.amount / question.outcome_probs[0]
        expected_stake_no = 0
        assert pos[0] == expected_stake_yes
        assert pos[1] == expected_stake_no

        # Verify that the user's budget was updated.
        cur.execute("SELECT budget FROM users WHERE id = ?", (1,))
        new_budget = cur.fetchone()[0]
        expected_budget = (
            1000000 - transaction.amount
        )  # Assuming budget_delta = -amount.
        assert new_budget == expected_budget


def test_perform_transaction_with_new_position_buy():
    # Test when no prior position exists (position is None) and transaction is a buy (answer True)
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        # Insert user
        insert_user(conn, User(id=1, username="Alice", budget=1000000))

        # Create a transaction for buying "Yes" stakes for question 101
        transaction = Transaction(
            user_id=1,
            question_id=101,
            transaction_type="buy",
            answer=True,  # Buying for "Yes"
            amount=100,
        )

        # Create the question with specific outcome probabilities (e.g., price for Yes = 0.8, for No = 0.2)
        question = Question(
            id=101,
            question="Will it rain tomorrow?",
            outcome_probs=[0.8, 0.2],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Test question",
        )

        # No existing position; perform_transaction should create one.
        perform_transaction(conn, transaction, None, question)

        # Verify transaction record inserted
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE user_id = ? AND question_id = ?",
            (1, 101),
        )
        assert cur.fetchone()[0] == 1

        # Verify new position: stake_yes should be increased by (amount / price)
        cur.execute(
            "SELECT stake_yes, stake_no FROM positions WHERE user_id = ? AND question_id = ?",
            (1, 101),
        )
        pos = cur.fetchone()
        expected_stake_yes = 0 + (transaction.amount / question.outcome_probs[0])
        expected_stake_no = 0
        assert pos[0] == expected_stake_yes
        assert pos[1] == expected_stake_no

        # Verify user budget is decreased by transaction.amount
        cur.execute("SELECT budget FROM users WHERE id = ?", (1,))
        new_budget = cur.fetchone()[0]
        assert new_budget == 1000000 - transaction.amount


def test_perform_transaction_with_existing_position_sell():
    # Test when a position exists and transaction is a sell (answer False)
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        # Insert user
        insert_user(conn, User(id=2, username="Bob", budget=1000000))

        # Insert an initial position for user 2, question 202
        initial_position = Position(
            user_id=2, question_id=202, stake_yes=150, stake_no=75
        )
        insert_position(conn, initial_position)

        # Create question with outcome_probs (price for Yes = 0.7, for No = 0.3)
        question = Question(
            id=202,
            question="Will the market rise?",
            outcome_probs=[0.7, 0.3],
            outcomes=["Yes", "No"],
            tag="Finance",
            outcome=None,
            end_date=datetime(2025, 6, 1),
            description="Market question",
        )

        # Create a transaction for selling "No" stakes (answer False)
        transaction = Transaction(
            user_id=2,
            question_id=202,
            transaction_type="sell",
            answer=False,  # Selling "No" stake
            amount=question.outcome_probs[1] * initial_position.stake_no,
        )

        perform_transaction(conn, transaction, initial_position, question)

        # Verify transaction inserted
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE user_id = ? AND question_id = ?",
            (2, 202),
        )
        assert cur.fetchone()[0] == 1

        expected_stake_no = initial_position.stake_no - (
            transaction.amount / question.outcome_probs[1]
        )
        expected_stake_yes = initial_position.stake_yes
        cur.execute(
            "SELECT stake_yes, stake_no FROM positions WHERE user_id = ? AND question_id = ?",
            (2, 202),
        )
        pos = cur.fetchone()
        assert pos[0] == expected_stake_yes
        assert pos[1] == expected_stake_no

        # Verify budget is decreased by transaction.amount (or increased if selling yields profit depending on logic)
        cur.execute("SELECT budget FROM users WHERE id = ?", (2,))
        new_budget = cur.fetchone()[0]
        # Assuming budget_delta is simply -transaction.amount here
        assert new_budget == 1000000 + transaction.amount


def test_perform_transaction_mismatched_question_id():
    # Test that perform_transaction asserts if question_id in position doesn't match transaction and question.
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        insert_user(conn, User(id=3, username="Carol", budget=1000000))

        # Create a valid position for question 303
        position = Position(user_id=3, question_id=303, stake_yes=100, stake_no=50)
        insert_position(conn, position)

        # Create a transaction for a different question (304)
        transaction = Transaction(
            user_id=3, question_id=304, transaction_type="buy", answer=True, amount=100
        )

        question = Question(
            id=303,  # Mismatch: position and question have 303, but transaction has 304
            question="Mismatch question?",
            outcome_probs=[0.6, 0.4],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 12, 31),
            description="Mismatch test",
        )

        import pytest

        with pytest.raises(AssertionError):
            perform_transaction(conn, transaction, position, question)


def test_perform_transaction_mismatched_user_id():
    # Test that perform_transaction asserts if user_id in position doesn't match transaction.
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        insert_user(conn, User(id=4, username="Dave", budget=1000000))

        # Create a valid position for user 4, question 404
        position = Position(user_id=4, question_id=404, stake_yes=80, stake_no=20)
        insert_position(conn, position)

        # Create a transaction with mismatched user_id (e.g., 5 instead of 4)
        transaction = Transaction(
            user_id=5, question_id=404, transaction_type="buy", answer=True, amount=150
        )

        question = Question(
            id=404,
            question="User mismatch test?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="Politics",
            outcome=None,
            end_date=datetime(2025, 11, 11),
            description="Mismatch test",
        )

        import pytest

        with pytest.raises(AssertionError):
            perform_transaction(conn, transaction, position, question)
