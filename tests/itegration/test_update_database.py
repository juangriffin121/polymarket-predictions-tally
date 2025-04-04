from datetime import datetime
import sqlite3

import click
from click.testing import CliRunner
from polymarket_predictions_tally.database.utils import load_sql_query
from polymarket_predictions_tally.database.write import (
    insert_question,
    insert_response,
    insert_user,
)
from polymarket_predictions_tally.logic import Position, Question, Response, User
from polymarket_predictions_tally import api
from polymarket_predictions_tally.integration import update_database
from tests.database.test_perform_transaction import insert_position


def fake_get_questions_by_id_list(question_ids):
    return [
        Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.6, 0.4],
            outcomes=["Yes", "No"],
            tag="weather",
            outcome=None,
            end_date=datetime(2025, 4, 1),
            description="Predicting tomorrow's weather",
        ),
        Question(
            id=2,
            question="Will the stock market go up?",
            outcome_probs=[1.0, 0.0],
            outcomes=["Yes", "No"],
            tag="finance",
            outcome=True,
            end_date=datetime(2025, 4, 2),
            description="Stock market prediction",
        ),
    ]


@click.command
def helper_cmd():
    with sqlite3.connect(":memory:") as conn:
        start_db = load_sql_query("setup.sql")
        conn.executescript(start_db)

        alice = User(id=1, username="Alice", budget=1000)

        old_q1 = Question(
            id=1,
            question="Will it rain tomorrow?",
            outcome_probs=[0.8, 0.2],
            outcomes=["Yes", "No"],
            tag="weather",
            outcome=None,
            end_date=datetime(2025, 4, 1),
            description="Predicting tomorrow's weather",
        )
        old_q2 = Question(
            id=2,
            question="Will the stock market go up?",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="finance",
            outcome=None,
            end_date=datetime(2025, 4, 2),
            description="Stock market prediction",
        )
        r1 = Response(
            user_id=1,
            question_id=1,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation="",
        )
        r2 = Response(
            user_id=1,
            question_id=2,
            answer="Yes",
            timestamp=datetime.now(),
            correct=None,
            explanation="",
        )

        p1 = Position(user_id=1, question_id=1, stake_yes=10.0, stake_no=0.0)
        p2 = Position(user_id=1, question_id=2, stake_yes=0.0, stake_no=20.0)

        insert_user(conn, alice)
        insert_question(conn, old_q1)
        insert_question(conn, old_q2)
        insert_response(conn, r1)
        insert_response(conn, r2)
        insert_position(conn, p1)
        insert_position(conn, p2)
        # Now when update_database() calls api.get_questions_by_id_list,
        # it will use our fake data.
        update_database(conn)


def test_update_database_positions(monkeypatch):
    # Monkeypatch the api module's function with our fake function.
    monkeypatch.setattr(api, "get_questions_by_id_list", fake_get_questions_by_id_list)
    runner = CliRunner()
    result = runner.invoke(helper_cmd)
    # print(result.output)

    # q1 (out: None, y: .8, n: .2) -> (out: None, y: .6, n: .4) dy = -.2
    # q2 (out: None, y: .5, n: .5) -> (out: True, y: 1., n: .0) dn -.5

    # s1y = 10 -> profit: 10 * dy -> -2
    # s1n = 20 -> profit: 20 * dn -> -10
    # net_profit = -12

    output = """User Alice had 1 right and 0 wrong
Detailed description:
\tQuestion: Will the stock market go up? [Yes]
Alice
Question: Will it rain tomorrow? StakeYes: 10.0 DeltaYes: -0.2 StakeNo: 0.0 DeltaNo: 0.2 Profit: -2.0 
Question: Will the stock market go up? StakeYes: 0.0 DeltaYes: 0.5 StakeNo: 20.0 DeltaNo: -0.5 Profit: -10.0 Sold
NetProfit: -12.0"""
    assert output.strip() == result.output.strip()
