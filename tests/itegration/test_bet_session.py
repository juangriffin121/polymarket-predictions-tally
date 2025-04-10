from datetime import datetime
import sqlite3
import click
from click.testing import CliRunner

from polymarket_predictions_tally import api
from polymarket_predictions_tally.constants import MAX_QUESTIONS
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import insert_user
from polymarket_predictions_tally.integration import (
    bet,
    history,
    update_database,
)
from polymarket_predictions_tally.logic import Question, User


def test_bet_session(monkeypatch):
    monkeypatch.setattr(api, "get_questions", fake_get_questions)
    monkeypatch.setattr(api, "get_questions_by_id_list", fake_get_questions_by_id_list)
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)
        alice = User(id=1, username="Alice", budget=1000)
        insert_user(conn, alice)
        runner = CliRunner()

        input = "1\ny\n100\n"
        bet_stdout = runner.invoke(bet_cmd, obj=conn, input=input)
        print(bet_stdout.output)

        # assert spending money reduces alices budget
        cursor = conn.cursor()
        results = cursor.execute(
            "SELECT budget FROM users WHERE username = ?", (alice.username,)
        )
        budget = results.fetchone()[0]
        expected_budget = alice.budget - 100.0
        assert budget == expected_budget

        update_databse_stdout = runner.invoke(update_database_cmd, obj=conn)
        print(update_databse_stdout.output)
        expected_stdout = """Alice
Question: Will it rain tomorrow? StakeYes: 200.0 DeltaYes: 0.5 StakeNo: 0.0 DeltaNo: -0.5 Profit: 100.0 Sold
NetProfit: 100.0"""

        # make sure the question is updated correctly
        assert update_databse_stdout.output.strip() == expected_stdout
        cursor = conn.cursor()
        results = cursor.execute(
            "SELECT budget FROM users WHERE username = ?", (alice.username,)
        )
        budget = results.fetchone()[0]
        expected_budget = alice.budget + 100.0
        assert budget == expected_budget
        # We need that resolved questions automatically get sold
        # also selling stock prompt


def fake_get_questions_by_id_list(question_ids):
    return [
        Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[1.0, 0.0],
            outcomes=["Yes", "No"],
            tag="weather",
            outcome=True,
            end_date=datetime(2025, 4, 1),
            description="Predicting tomorrow's weather",
        ),
    ]


def fake_get_questions(tag: str, limit: int = MAX_QUESTIONS) -> list[Question]:
    return [
        Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="weather",
            outcome=None,
            end_date=datetime(2025, 4, 1),
            description="Predicting tomorrow's weather",
        ),
        Question(
            id=2,
            question="Will the stock market go up?",
            outcome_probs=[0.4, 0.6],
            outcomes=["Yes", "No"],
            tag="finance",
            outcome=None,
            end_date=datetime(2025, 4, 2),
            description="Stock market prediction",
        ),
        Question(
            id=3,
            question="Will AI replace us?",
            outcome_probs=[0.9, 0.1],
            outcomes=["Yes", "No"],
            tag="finance",
            outcome=None,
            end_date=datetime(2025, 4, 2),
            description="AIs future",
        ),
    ]


@click.command
@click.pass_obj
def bet_cmd(conn):
    bet("Alice", conn)


@click.command
@click.pass_obj
def history_cmd(conn):
    history("Alice", conn)


@click.command
@click.pass_obj
def update_database_cmd(conn):
    update_database(conn)
