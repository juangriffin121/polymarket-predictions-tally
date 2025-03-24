from datetime import datetime
import click
from click.testing import CliRunner

from polymarket_predictions_tally.cli.user_input import process_bet
from polymarket_predictions_tally.logic import Position, Question, User


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

    position = Position(user_id=1, question_id=2, stake_yes=10.0, stake_no=0.0)
    _, transaction, _ = process_bet(user, [question1, question2], [None, position])
    if transaction is not None:
        click.echo(f"Responded: {transaction.question_id}")
        click.echo(f"Answer: {transaction.answer}")
        click.echo(f"Bet: {transaction.amount}")
    else:
        click.echo("No new transactions were processed")


def test_process_prediction_cmd():
    runner = CliRunner()
    result = runner.invoke(process_prediction_cmd, input="1\ny\n100")
    # print(result.output)
    assert "Responded: 1" in result.output
    assert "Answer: True" in result.output
    assert "Bet: 100.0" in result.output

    result = runner.invoke(process_prediction_cmd, input="2\ny\nsell\n5\n")
    print(result.output)
    assert "Responded: 2" in result.output
    assert "Answer: True" in result.output
    assert "Bet: 5.0" in result.output

    result = runner.invoke(process_prediction_cmd, input="2\ny\nsell\n11\nn\n")
    print(result.output)
    assert "No new transactions were processed" in result.output
