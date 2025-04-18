import sqlite3
from polymarket_predictions_tally import api
from polymarket_predictions_tally.cli import prints
from polymarket_predictions_tally.cli.prints import (
    inform_users_of_change,
    inform_users_of_stocks_change,
)
from polymarket_predictions_tally.cli.user_input import (
    process_bet,
    process_prediction,
    prompt_sell,
)
from polymarket_predictions_tally.constants import MAX_QUESTIONS
from polymarket_predictions_tally.database import read
from polymarket_predictions_tally.database.read import (
    get_active_question_ids,
    get_all_responses_to_questions,
    get_all_users,
    get_latest_responses_to_questions,
    get_previous_user_responses,
    get_questions_from_ids,
    get_responses,
    get_stats,
    get_updated_positions,
    get_user,
    get_user_positions,
    get_users_affected_by_update,
)
from polymarket_predictions_tally.database.write import (
    get_or_make_user,
    insert_question,
    insert_response,
    perform_transaction,
    resolve_updated_positions,
    update_present_questions,
    update_questions,
    update_responses,
    update_users_stats,
)


def predict(username: str, conn):
    user = get_or_make_user(conn, username)
    api_questions = api.get_questions(tag="Politics", limit=MAX_QUESTIONS)
    update_present_questions(conn, api_questions)
    previous_user_responses = get_previous_user_responses(conn, api_questions, user.id)
    question, response = process_prediction(
        user, api_questions, previous_user_responses
    )
    if response is not None:
        insert_question(conn, question)
        insert_response(conn, response)


def update_database(conn: sqlite3.Connection):
    question_ids = get_active_question_ids(conn)
    updated_questions = api.get_questions_by_id_list(question_ids)
    old_questions = get_questions_from_ids(conn, question_ids)
    update_questions(conn, updated_questions)

    # update predictions
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

    # update bets
    updated_positions = get_updated_positions(conn, updated_questions)
    users = get_all_users(conn)
    users = {user.id: user for user in users}
    inform_users_of_stocks_change(
        users, updated_positions, updated_questions, old_questions, resolved_questions
    )
    resolve_updated_positions(conn, resolved_questions)


def history(username: str, conn: sqlite3.Connection):
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


def show_users(conn: sqlite3.Connection):
    users = get_all_users(conn)
    prints.users(users)


def bet(username: str, conn: sqlite3.Connection):
    user = get_or_make_user(conn, username)
    api_questions = api.get_questions(tag="Politics", limit=MAX_QUESTIONS)
    update_present_questions(conn, api_questions)
    user_positions = get_user_positions(conn, api_questions, user.id)
    question, transaction, position = process_bet(user, api_questions, user_positions)
    if transaction is not None:
        insert_question(conn, question)
        perform_transaction(conn, transaction, position, question)


def sell(username: str, conn: sqlite3.Connection):
    user = get_user(conn, username)
    assert user is not None
    positions = read.get_all_user_positions(conn, user.id)
    questions = read.get_questions_from_positions(conn, positions)
    transaction, position, question = prompt_sell(user, positions, questions)
    if transaction:
        perform_transaction(conn, transaction, position, question)
