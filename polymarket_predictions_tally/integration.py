import sqlite3
from typing import Optional

from polymarket_predictions_tally.api import get_questions
from polymarket_predictions_tally.cli import (
    prompt_for_response,
    prompt_question_selection,
)
from polymarket_predictions_tally.database import (
    get_previous_user_responses,
    update_present_questions,
)
from polymarket_predictions_tally.logic import Question, Response, User


def process_prediction(
    conn: sqlite3.Connection,
    user: User,
    api_questions: list[Question],
    mode: str = "predict",
) -> Optional[Response]:
    update_present_questions(conn, api_questions)
    previous_user_responses = get_previous_user_responses(conn, api_questions, user.id)
    [chosen_question, previous_user_response] = prompt_question_selection(
        api_questions, previous_user_responses, mode
    )
    return prompt_for_response(user, chosen_question, previous_user_response)

