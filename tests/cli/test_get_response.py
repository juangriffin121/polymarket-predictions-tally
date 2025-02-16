from datetime import datetime
import click

from click.testing import CliRunner
from polymarket_predictions_tally.cli.user_input import get_response
from polymarket_predictions_tally.logic import Question, User


@click.command()
def get_response_cmd():
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
    response = get_response(user, question)
    click.echo(f"{response.answer}\n{response.explanation}")


def test_get_response():
    runner = CliRunner()
    result = runner.invoke(get_response_cmd, input="\n".join(["y", "n"]))
    print(result.output)
    assert result.exit_code == 0
    assert "Yes" in result.output
