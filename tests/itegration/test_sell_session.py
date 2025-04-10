from datetime import datetime
import sqlite3

import click
from click.testing import CliRunner

from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_question, insert_user
from polymarket_predictions_tally.integration import sell
from polymarket_predictions_tally.logic import Position, Question, User
from tests.database.test_perform_transaction import insert_position


def test_sell_session():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        alice = User(id=1, username="Alice", budget=1000)
        insert_user(conn, alice)

        q1 = Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.8, 0.2],
            outcomes=["Yes", "No"],
            tag="weather",
            outcome=None,
            end_date=datetime(2025, 4, 1),
            description="Predicting tomorrow's weather",
        )
        q2 = Question(
            id=2,
            question="Will the stock market go up?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="finance",
            outcome=None,
            end_date=datetime(2025, 4, 2),
            description="Stock market prediction",
        )

        p1 = Position(user_id=1, question_id=1, stake_yes=10.0, stake_no=0.0)
        p2 = Position(user_id=1, question_id=2, stake_yes=0.0, stake_no=20.0)
        insert_question(conn, q1)
        insert_question(conn, q2)
        insert_position(conn, p1)
        insert_position(conn, p2)

        runner = CliRunner()
        input = "1\ny\nsell\n8\n"
        result = runner.invoke(sell_cmd, obj=(alice.username, conn), input=input)
        print((result.output))

        cursor = conn.cursor()
        results = cursor.execute(
            "SELECT budget FROM users WHERE username = ?", (alice.username,)
        )
        budget = results.fetchone()[0]
        expected_budget = alice.budget + 8.0
        assert budget == expected_budget
        # assert False


@click.command
@click.pass_obj
def sell_cmd(ctx):
    username, conn = ctx
    sell(username, conn)
