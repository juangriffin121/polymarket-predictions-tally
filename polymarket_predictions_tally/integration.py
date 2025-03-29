import sqlite3
from polymarket_predictions_tally import api
from polymarket_predictions_tally.cli import prints
from polymarket_predictions_tally.cli.prints import inform_users_of_change
from polymarket_predictions_tally.cli.user_input import (
    process_bet,
    process_prediction,
)
from polymarket_predictions_tally.constants import MAX_QUESTIONS
from polymarket_predictions_tally.database.read import (
    get_active_question_ids,
    get_all_responses_to_questions,
    get_all_users,
    get_latest_responses_to_questions,
    get_previous_user_responses,
    get_questions_from_ids,
    get_responses,
    get_stats,
    get_user,
    get_user_positions,
    get_users_affected_by_update,
)
from polymarket_predictions_tally.database.write import (
    get_or_make_user,
    insert_question,
    insert_response,
    perform_transaction,
    update_present_questions,
    update_questions,
    update_responses,
    update_users_stats,
)
from polymarket_predictions_tally.initialization import DB_PATH
from polymarket_predictions_tally.logic import Transaction


def run_user_session(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        user = get_or_make_user(conn, username)
        api_questions = api.get_questions(tag="Politics", limit=MAX_QUESTIONS)
        update_present_questions(conn, api_questions)
        previous_user_responses = get_previous_user_responses(
            conn, api_questions, user.id
        )
        question, response = process_prediction(
            user, api_questions, previous_user_responses
        )
        if response is not None:
            insert_question(conn, question)
            insert_response(conn, response)


def update_database():
    with sqlite3.connect(DB_PATH) as conn:
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
        update_users_stats(conn, update_effects_info)


def history(username):
    with sqlite3.connect(DB_PATH) as conn:
        user = get_user(conn, username)
        if user is None:
            prints.user_not_in_db(username)
            return

        responses = get_responses(conn, user.id)
        questions = get_questions_from_ids(
            conn, [response.question_id for response in responses]
        )
        stats = get_stats(conn, user.id)

        prints.history(user, responses, questions, stats)


def show_users():
    with sqlite3.connect(DB_PATH) as conn:
        users = get_all_users(conn)
        prints.users(users)


def bet(username):
    with sqlite3.connect(DB_PATH) as conn:
        user = get_or_make_user(conn, username)
        api_questions = api.get_questions(tag="Politics", limit=MAX_QUESTIONS)
        update_present_questions(conn, api_questions)
        user_positions = get_user_positions(conn, api_questions, user.id)
        question, transaction, position = process_bet(
            user, api_questions, user_positions
        )
        if transaction is not None:
            insert_question(conn, question)
            perform_transaction(conn, transaction, position, question)
