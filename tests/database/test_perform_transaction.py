import sqlite3

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_user, perform_transaction
from polymarket_predictions_tally.logic import Position, Transaction, User


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

        # Perform the transaction.
        perform_transaction(conn, transaction, None)

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
        expected_stake_yes = 0 + transaction.amount
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


"""
def test_perform_transaction_invalid_user_id():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        # Insert a user and a position for user 1.
        insert_user(conn, User(id=1, username="Alice", budget=1000000))
        initial_position = Position(
            user_id=1, question_id=101, stake_yes=200, stake_no=50
        )
        insert_position(conn, initial_position)

        # Create a transaction with a mismatched user_id (e.g., 2 instead of 1)
        transaction = Transaction(
            user_id=2, question_id=101, transaction_type="buy", answer=True, amount=100
        )

        # Expect an assertion error due to mismatched user_id.
        import pytest

        with pytest.raises(AssertionError):
            perform_transaction(conn, transaction, initial_position)

"""
