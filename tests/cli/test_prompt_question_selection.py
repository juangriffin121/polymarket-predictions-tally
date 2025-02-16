from typing import Optional
import click
from click.testing import CliRunner
from datetime import datetime

from polymarket_predictions_tally.cli.user_input import prompt_question_selection
from polymarket_predictions_tally.logic import Question, Response


# Dummy click command that wraps prompt_question_selection
@click.command()
def select_question_cmd():
    # Create a list of dummy questions for testing.
    questions = [
        Question(
            id=1,
            question="Question 1",
            outcome_probs=[0.5, 0.5],
            outcomes=["Yes", "No"],
            tag="dummy",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Desc 1",
        ),
        Question(
            id=2,
            question="Question 2",
            outcome_probs=[0.6, 0.4],
            outcomes=["Yes", "No"],
            tag="dummy",
            outcome=None,
            end_date=datetime(2025, 1, 1),
            description="Desc 2",
        ),
    ]
    # For simplicity, assume no previous responses
    responses: list[Optional[Response]] = [None, None]
    mode = "predict"

    # Call the function that we're testing
    chosen_question, previous_response = prompt_question_selection(
        questions, responses, mode
    )

    # For testing purposes, output the chosen question's id
    click.echo(f"Chosen: {chosen_question.id}")


def test_prompt_question_selection_cmd():
    runner = CliRunner()
    # Simulate the user selecting the second question.
    # This input should match what your prompt logic expects.
    result = runner.invoke(select_question_cmd, input="2\n")

    # Check that the command ran successfully and that the expected output is there.
    assert result.exit_code == 0
    assert "Chosen: 2" in result.output
