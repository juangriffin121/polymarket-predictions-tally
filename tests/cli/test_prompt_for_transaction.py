from datetime import datetime
import click
from click.testing import CliRunner

from polymarket_predictions_tally.cli.user_input import prompt_for_transaction
from polymarket_predictions_tally.logic import Question, Position, User


@click.command
def prompt_for_transaction_cmd():
    user = User(id=1, username="Alice", budget=100)
    question = Question(
        id=2,
        question="Will Julius Caesar win the 100 BC roman dictatorial election?",
        outcome_probs=[0.9, 0.1],
        outcomes=["Yes", "No"],
        end_date=datetime(100, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )
    position = Position(user_id=1, question_id=2, stake_yes=10.0, stake_no=5.0)

    _, new_transaction, _ = prompt_for_transaction(user, question, position)
    if new_transaction is not None:
        click.echo(f"Your new answer:\n\t{new_transaction}")
    else:
        click.echo("No changes made")


def test_prompt_for_transaction_change():
    runner = CliRunner()
    result = runner.invoke(prompt_for_transaction_cmd, input="y\nsell\n4")
    print(result.output)
    assert (
        f"Your new answer:\n\tTransaction(user_id=1, question_id=2, transaction_type='sell', answer=True, amount=4.0)"
        in result.output
    )


@click.command
def prompt_for_transaction_cmd_no_prev():
    user = User(id=1, username="Alice", budget=100)
    question = Question(
        id=2,
        question="Will Julius Caesar win the 100 BC roman dictatorial election?",
        outcome_probs=[0.9, 0.1],
        outcomes=["Yes", "No"],
        end_date=datetime(100, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )

    _, new_transaction, _ = prompt_for_transaction(user, question, None)
    if new_transaction is not None:
        click.echo(f"Your new answer:\n\t{new_transaction}")
    else:
        click.echo("No changes made")


def test_prompt_for_transaction_no_prev():
    runner = CliRunner()
    result = runner.invoke(prompt_for_transaction_cmd_no_prev, input="n\n100")
    print(result.output)
    assert (
        f"Your new answer:\n\tTransaction(user_id=1, question_id=2, transaction_type='buy', answer=False, amount=100.0)"
        in result.output
    )
