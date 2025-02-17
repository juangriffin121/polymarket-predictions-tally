from datetime import datetime
import click
from click.testing import CliRunner

from polymarket_predictions_tally.cli.user_input import process_prediction
from polymarket_predictions_tally.logic import Question, Response, User


@click.command
def process_prediction_cmd():
    user = User(id=1, username="Alice", budget=100)
    question1 = Question(
        id=1,
        question="Will Julius Caesar win the 100 BC roman dictatorial election?",
        outcome_probs=[90.0, 10.0],
        outcomes=["Yes", "No"],
        end_date=datetime(100, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )
    question2 = Question(
        id=2,
        question="Will Alexander the Great win the 500 BC macedonian dictatorial election?",
        outcome_probs=[90.0, 10.0],
        outcomes=["Yes", "No"],
        end_date=datetime(500, 10, 10),
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
    _, response = process_prediction(
        user, [question1, question2], [None, previous_response]
    )
    if response is not None:
        click.echo(f"Responded: {response.question_id}")
        click.echo(f"Answer: {response.answer}")
    else:
        click.echo("No new responses were given")


def test_process_prediction_cmd():
    runner = CliRunner()
    result = runner.invoke(process_prediction_cmd, input="1\ny\nn\n")
    assert "Responded: 1" in result.output
    assert "Answer: Yes" in result.output

    result = runner.invoke(process_prediction_cmd, input="2\ny\nn\nn\n")
    assert "Responded: 2" in result.output
    assert "Answer: No" in result.output
