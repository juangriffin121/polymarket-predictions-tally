from datetime import datetime
import click
from click.testing import CliRunner

from polymarket_predictions_tally.cli import prompt_for_response
from polymarket_predictions_tally.logic import Question, Response, User


@click.command
def prompt_for_response_cmd():
    user = User(id=1, username="Alice", budget=100)
    question = Question(
        id=2,
        question="Will Julius Caesar win the 100 BC roman dictatorial election?",
        outcome_probs=[90.0, 10.0],
        outcomes=["Yes", "No"],
        end_date=datetime(100, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )
    previous_response = Response(
        user_id=1,
        question_id=2,
        answer="Yes",
        timestamp=datetime.now(),
        correct=None,
        explanation=None,
    )

    new_response = prompt_for_response(user, question, previous_response)
    if new_response is not None:
        click.echo(f"Your new answer: {new_response.answer}")
    else:
        click.echo("No changes made")


def test_prompt_for_response_no_changing():
    runner = CliRunner()
    result = runner.invoke(prompt_for_response_cmd, input="n")
    assert "No changes made" in result.output


def test_prompt_for_response_change():
    runner = CliRunner()
    result = runner.invoke(prompt_for_response_cmd, input="y\nn\nn\n")
    assert "Your new answer: No" in result.output


@click.command
def prompt_for_response_cmd_no_prev():
    user = User(id=1, username="Alice", budget=100)
    question = Question(
        id=2,
        question="Will Julius Caesar win the 100 BC roman dictatorial election?",
        outcome_probs=[90.0, 10.0],
        outcomes=["Yes", "No"],
        end_date=datetime(100, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )

    new_response = prompt_for_response(user, question, previous_response=None)
    if new_response is not None:
        click.echo(f"Your new answer: {new_response.answer}")
    else:
        click.echo("No changes made")


def test_prompt_for_response_no_prev():
    runner = CliRunner()
    result = runner.invoke(prompt_for_response_cmd_no_prev, input="n\nn\n")
    assert "Your new answer: No" in result.output
