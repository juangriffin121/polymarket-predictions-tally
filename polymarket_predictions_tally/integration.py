import sqlite3
import click
from polymarket_predictions_tally.api import get_questions
from polymarket_predictions_tally.cli.user_input import (
    process_prediction,
)
from polymarket_predictions_tally.database.read import get_previous_user_responses
from polymarket_predictions_tally.database.write import (
    get_or_make_user,
    insert_question,
    insert_response,
    update_present_questions,
)


def run_user_session(username: str, mode: str = "predict"):
    with sqlite3.connect("./database/database.db") as conn:
        click.echo("enters 1")
        user = get_or_make_user(conn, username)
        print("enters 2")
        api_questions = get_questions(tag="Politics", limit=10)
        print("enters 3")
        update_present_questions(conn, api_questions)
        print("enters 4")
        previous_user_responses = get_previous_user_responses(
            conn, api_questions, user.id
        )
        print("enters 5")
        question, response = process_prediction(
            user, api_questions, previous_user_responses, mode
        )
        print("enters 6")
        if response is not None:
            insert_question(conn, question)
            insert_response(conn, response)

        print("enters 7")
