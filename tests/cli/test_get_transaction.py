from datetime import datetime
import click
from click.testing import CliRunner

from polymarket_predictions_tally.cli.user_input import get_transaction
from polymarket_predictions_tally.logic import Position, Question, User


@click.command
def get_transaction_cmd():
    user = User(1, "Alice", 10000)
    question = Question(
        id=2,
        question="Will Trump kill Alice the user before 2026?",
        outcome_probs=[90.0, 10.0],
        outcomes=["Yes", "No"],
        end_date=datetime(2026, 1, 1),
        outcome=None,
        description="",
        tag="Politics",
    )
    position = Position(user_id=1, question_id=2, stake_yes=20.0, stake_no=10.0)
    transaction = get_transaction(user, question, position)
    click.echo(f"{transaction}")


@click.command
def get_transaction_cmd_no_stake():
    user = User(1, "Alice", 10000)
    question = Question(
        id=2,
        question="Will Trump kill Alice the user before 2026?",
        outcome_probs=[90.0, 10.0],
        outcomes=["Yes", "No"],
        end_date=datetime(2026, 1, 1),
        outcome=None,
        description="",
        tag="Politics",
    )
    position = Position(user_id=1, question_id=2, stake_yes=0.0, stake_no=0.0)
    transaction = get_transaction(user, question, position)
    click.echo(f"{transaction}")


def test_get_transaction():
    runner = CliRunner()
    result = runner.invoke(get_transaction_cmd, input="y\nbuy\n100")
    print(result.output)
    assert result.exit_code == 0
    assert (
        "Transaction(user_id=1, question_id=2, transaction_type='buy', answer=True, amount=100.0)"
        in result.output
    )


def test_get_transaction_no_stake():
    runner = CliRunner()
    result = runner.invoke(get_transaction_cmd_no_stake, input="y\n200\n")
    print(result.output)
    assert result.exit_code == 0
    assert (
        "Transaction(user_id=1, question_id=2, transaction_type='buy', answer=True, amount=200.0)"
        in result.output
    )
