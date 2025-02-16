import sqlite3

from polymarket_predictions_tally.api import get_questions
from polymarket_predictions_tally.cli.user_input import (
    process_prediction,
)
from polymarket_predictions_tally.database import (
    get_previous_user_responses,
    insert_response,
    update_present_questions,
)
from polymarket_predictions_tally.logic import User


def run_user_session(conn: sqlite3.Connection, user: User, mode: str = "predict"):
    api_questions = get_questions(tag="Politics", limit=10)
    update_present_questions(conn, api_questions)
    previous_user_responses = get_previous_user_responses(conn, api_questions, user.id)
    response = process_prediction(user, api_questions, previous_user_responses, mode)
    if response is not None:
        insert_response(conn, response)
