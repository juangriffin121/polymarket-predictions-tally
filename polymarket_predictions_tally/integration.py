import sqlite3
from polymarket_predictions_tally import api, utils
from polymarket_predictions_tally.cli.prints import inform_users_of_change
from polymarket_predictions_tally.cli.user_input import (
    process_prediction,
)
from polymarket_predictions_tally.database.read import (
    get_active_question_ids,
    get_all_responses_to_questions,
    get_latest_responses_to_questions,
    get_previous_user_responses,
    get_user,
    get_user_from_id,
    get_users_affected_by_update,
)
from polymarket_predictions_tally.database.write import (
    get_or_make_user,
    insert_question,
    insert_response,
    update_present_questions,
    update_questions,
    update_responses,
)


def run_user_session(username: str, mode: str = "predict"):
    with sqlite3.connect("./database/database.db") as conn:
        user = get_or_make_user(conn, username)
        api_questions = api.get_questions(tag="Politics", limit=10)
        update_present_questions(conn, api_questions)
        previous_user_responses = get_previous_user_responses(
            conn, api_questions, user.id
        )
        question, response = process_prediction(
            user, api_questions, previous_user_responses, mode
        )
        if response is not None:
            insert_question(conn, question)
            insert_response(conn, response)


def update_database():
    with sqlite3.connect("./database/database.db") as conn:
        question_ids = get_active_question_ids(conn)
        updated_questions = api.get_questions_by_id_list(question_ids)
        update_questions(conn, updated_questions)
        resolved_questions = [
            question
            for question in updated_questions
            if question and question.outcome is not None
        ]
        all_responses = get_all_responses_to_questions(conn, resolved_questions)
        update_responses(conn, all_responses, resolved_questions)

        latest_responses = get_latest_responses_to_questions(conn, resolved_questions)
        update_effects_info = get_users_affected_by_update(
            conn,
            latest_responses,
            resolved_questions,
        )
        inform_users_of_change(update_effects_info, resolved_questions)
