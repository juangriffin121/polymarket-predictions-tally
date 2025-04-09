from datetime import datetime
import click
from click.testing import CliRunner
from polymarket_predictions_tally.cli.user_input import choose_position
from polymarket_predictions_tally.logic import Position, Question


def test_choose_position():
    questions = [
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

    positions = [
        Position(user_id=1, question_id=1, stake_yes=10.0, stake_no=0.0),
        Position(user_id=1, question_id=2, stake_yes=0.0, stake_no=10.0),
        Position(user_id=1, question_id=3, stake_yes=5.0, stake_no=5.0),
    ]
    runner = CliRunner()
    input = "1\nsell\ny\n100\n"
    result = runner.invoke(choose_position_cmd, obj=(positions, questions), input=input)
    print(result.output)
    expected_output = (
        """Position(user_id=1, question_id=1, stake_yes=10.0, stake_no=0.0)"""
    )
    assert expected_output.strip() in result.output.strip()
    expected_output = """Question 1: Will it rain tomorrow?"""
    assert expected_output.strip() in result.output.strip()


@click.command
@click.pass_obj
def choose_position_cmd(ctx):
    positions, questions = ctx
    position, question = choose_position(positions, questions)
    click.echo(position)
    click.echo(question)
