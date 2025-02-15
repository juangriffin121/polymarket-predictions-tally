import sqlite3
from typing import List, Optional

import click

from polymarket_predictions_tally.database import (
    has_user_answered,
    update_present_questions,
)
from polymarket_predictions_tally.logic import Question, Response, User


def process_prediction(
    conn: sqlite3.Connection,
    user: User,
    api_questions: List[Question],
    mode: str = "predict",
) -> Optional[Response]:
    update_present_questions(conn, api_questions)
    previous_user_responses = []
    for question in api_questions:
        response = has_user_answered(conn, user.id, question.id)
        previous_user_responses.append(response)
    [chosen_question, previous_user_response] = prompt_question_selection(
        api_questions, previous_user_responses, mode
    )
    return prompt_for_response(chosen_question, previous_user_response)


def prompt_question_selection(
    questions: List[Question], responses: list[Optional[Response]], mode: str
) -> tuple[Question, Optional[Response]]:
    options = []
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        status = f"[{response.answer}]" if response else ""
        options.append(f"{i}. {question.question} {status}".strip())

    # Prompt the user to select a question
    click.echo("\nAvailable Questions:\n" + "\n".join(options))

    choice = click.prompt(
        "Select a question by number", type=click.IntRange(1, len(questions))
    )

    # Return the selected question and its associated response
    return questions[choice - 1], responses[choice - 1]


def prompt_for_response(
    question: Question, previous_response: Optional[Response]
) -> Optional[Response]:
    """
    Prompts the user for an answer to the given question.

    If previous_response is provided, the prompt should show:
       "You answered [answer] to <question text>.
        Do you want to change your answer? [yes/no]"
    If the user chooses not to change their answer, return None.
    Otherwise, prompt the user to provide a new answer (e.g. "yes" or "no") and return it.
    """
    raise NotImplementedError
