from datetime import datetime
import click
from click.testing import CliRunner

from polymarket_predictions_tally.cli.user_input import process_bet
from polymarket_predictions_tally.logic import Position, Question, User


@click.command
def process_bet_cmd():
    user = User(id=1, username="Alice", budget=100)
    question1 = Question(
        id=1,
        question="Will Julius Caesar win the 100 BC roman dictatorial election?",
        outcome_probs=[0.9, 0.1],
        outcomes=["Yes", "No"],
        end_date=datetime(100, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )
    question2 = Question(
        id=2,
        question="Will Alexander the Great win the 500 BC macedonian dictatorial election?",
        outcome_probs=[0.9, 0.1],
        outcomes=["Yes", "No"],
        end_date=datetime(500, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )

    position = Position(user_id=1, question_id=2, stake_yes=10.0, stake_no=0.0)
    _, transaction, _ = process_bet(user, [question1, question2], [None, position])
    if transaction is not None:
        click.echo(f"Responded: {transaction.question_id}")
        click.echo(f"Answer: {transaction.answer}")
        click.echo(f"Bet: {transaction.amount}")
    else:
        click.echo("No new transactions were processed")


def test_process_bet():
    runner = CliRunner()
    result = runner.invoke(process_bet_cmd, input="1\ny\n100")
    # print(result.output)
    assert "Responded: 1" in result.output
    assert "Answer: True" in result.output
    assert "Bet: 100.0" in result.output

    result = runner.invoke(process_bet_cmd, input="2\ny\nsell\n5\n")
    print(result.output)
    assert "Responded: 2" in result.output
    assert "Answer: True" in result.output
    assert "Bet: 5.0" in result.output

    result = runner.invoke(process_bet_cmd, input="2\ny\nsell\n20\nn\n")
    print(result.output)
    assert "No new transactions were processed" in result.output


def test_process_bet_buy():
    # Simulate a scenario where the user selects the first question (which has no existing position),
    # confirms a "Yes" answer, and then enters a valid amount (100) to buy.
    runner = CliRunner()
    # Inputs: "1" to choose the first question, "y" to confirm the answer (buy), "100" as the amount.
    result = runner.invoke(process_bet_cmd, input="1\ny\n100\n")
    # Expect that the chosen question is the first one (id 1) and that a transaction is created.
    assert "Responded: 1" in result.output
    assert "Answer: True" in result.output
    assert "Bet: 100.0" in result.output


def test_process_bet_sell_existing():
    # Simulate a scenario where the user selects the second question, which already has an existing position.
    # In this test, the position exists (e.g., with some stake for "Yes"), so the user opts to sell.
    # Inputs: "2" to choose the second question, "y" to confirm answer, "sell" as the transaction type,
    # then "5" as the amount.
    runner = CliRunner()
    result = runner.invoke(process_bet_cmd, input="2\ny\nsell\n5\n")
    assert "Responded: 2" in result.output
    assert "Answer: True" in result.output
    assert "Bet: 5.0" in result.output


def test_process_bet_no_transaction():
    # Simulate a scenario where the user selects the second question and attempts a sell transaction,
    # but the amount entered exceeds their allowed limit (or is invalid), and then opts not to try again.
    # This should result in no new transaction being processed.
    runner = CliRunner()
    # Inputs: "2" to choose the second question, "y" to confirm answer,
    # then "sell" as the transaction type, "20" as the invalid amount, and finally "n" to not retry.
    result = runner.invoke(process_bet_cmd, input="2\ny\nsell\n20\nn\n")
    assert "No new transactions were processed" in result.output
