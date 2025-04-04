import json
from os import listdir
import sqlite3
from sqlite3.dbapi2 import Connection

from polymarket_predictions_tally.database.read import (
    get_positions_on_question,
    get_user,
    get_user_id_by_name,
    is_question_in_db,
    validate_response,
)
from polymarket_predictions_tally.database.utils import get_new_position, load_sql_query
from polymarket_predictions_tally.logic import (
    InvalidResponse,
    Position,
    Question,
    Transaction,
    User,
    Response,
)


def get_or_make_user(conn: sqlite3.Connection, username: str) -> User:
    user = get_user(conn, username)
    if user:
        return user
    else:
        insert_user_by_name(conn, username)
        user = get_user(conn, username)
        if user:
            return user
        else:
            raise Exception("Unreachable code")


def insert_user_by_name(conn: sqlite3.Connection, username: str):
    cursor = conn.cursor()
    query = load_sql_query("insert_user_by_name.sql")
    cursor.execute(query, (username,))
    user_id = get_user_id_by_name(conn, username)
    conn.commit()
    assert not user_id is None
    insert_default_stats(conn, user_id=user_id)
    conn.commit()


def remove_user(conn: sqlite3.Connection, id: int):
    cursor = conn.cursor()
    insert_user_query = load_sql_query("remove_user.sql")
    cursor.execute(insert_user_query, (id,))
    conn.commit()


def update_user(conn: sqlite3.Connection, id: int, new_budget: int):
    cursor = conn.cursor()
    update_user_query = load_sql_query("update_user.sql")
    cursor.execute(update_user_query, (new_budget, id))
    conn.commit()


def insert_user(conn: sqlite3.Connection, user: User):
    cursor = conn.cursor()
    insert_user_query = load_sql_query("insert_user.sql")
    cursor.execute(insert_user_query, (user.id, user.username, user.budget))
    insert_default_stats(conn, user_id=user.id)
    conn.commit()


def insert_response(conn: sqlite3.Connection, response: Response):
    params = (
        response.user_id,
        response.question_id,
        response.answer,
        response.timestamp,
        response.correct,
        response.explanation,
    )
    insert_response_query = load_sql_query("insert_response.sql")
    match validate_response(conn, response):
        case (True, True):
            cursor = conn.cursor()
            cursor.execute(insert_response_query, params)
            conn.commit()
        case (False, True):
            raise InvalidResponse(
                f"Invalid Response: Invalid user_id: {response.user_id}"
            )
        case (True, False):
            raise InvalidResponse(
                f"Invalid Response: Invalid question_id: {response.question_id}"
            )
        case (False, False):
            raise InvalidResponse(
                f"Invalid Response: Invalid question_id and user_id: {response.question_id}, {response.user_id}"
            )


def update_question(conn: sqlite3.Connection, question: Question):
    remove_question(conn, question.id)
    insert_question(conn, question)


def update_questions(conn: sqlite3.Connection, questions: list[Question | None]):
    for question in questions:
        if question:
            update_question(conn, question)


def update_present_questions(conn: sqlite3.Connection, api_questions: list[Question]):
    for question in api_questions:
        if is_question_in_db(conn, question.id):
            update_question(conn, question)


def remove_question(conn: sqlite3.Connection, id: int):
    remove_question_query = load_sql_query("remove_question.sql")
    cursor = conn.cursor()
    cursor.execute(remove_question_query, (id,))
    conn.commit()


def insert_question(conn: sqlite3.Connection, question: Question):
    # Convert lists to JSON strings
    outcome_probs_json = json.dumps(question.outcome_probs)
    outcomes_json = json.dumps(question.outcomes)

    insert_question_query = load_sql_query("insert_question.sql")
    cursor = conn.cursor()
    cursor.execute(
        insert_question_query,
        (
            question.id,
            question.question,
            question.tag,
            question.end_date,
            question.description,
            question.outcome,
            outcome_probs_json,
            outcomes_json,
        ),
    )

    # Commit the transaction
    conn.commit()


def update_responses(
    conn: sqlite3.Connection, responses: list[list[Response]], questions: list[Question]
):
    cursor = conn.cursor()
    query = load_sql_query("update_response.sql")

    for question, responses_to_question in zip(questions, responses):
        if not question.outcome:
            continue

        for response in responses_to_question:
            assert response.answer in ("Yes", "No")
            assert not question.outcome is None

            if question.outcome == True:
                correct_answer = "Yes"
            else:
                correct_answer = "No"

            correct = response.answer == correct_answer
            cursor.execute(
                query, (correct, question.id, response.user_id, response.timestamp)
            )


def insert_default_stats(conn: sqlite3.Connection, user_id: int):
    query = load_sql_query("insert_default_stats.sql")
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))


def update_user_stats(
    conn: sqlite3.Connection,
    user_id: int,
    new_correct_responses: int,
    new_incorrect_responses: int,
):
    query = load_sql_query("update_user_stats.sql")
    cursor = conn.cursor()
    cursor.execute(query, (new_correct_responses, new_incorrect_responses, user_id))


def update_users_stats(
    conn: sqlite3.Connection, update_info: dict[User, list[tuple[Response, bool]]]
):
    for user, info in update_info.items():
        right_count = sum([correct for _, correct in info])
        wrong_count = len(info) - right_count
        update_user_stats(conn, user.id, right_count, wrong_count)


def perform_transaction(
    conn: sqlite3.Connection,
    transaction: Transaction,
    position: Position | None,
    question: Question,
):
    if position is None:
        position = Position(
            user_id=transaction.user_id,
            question_id=transaction.question_id,
            stake_yes=0.0,
            stake_no=0.0,
        )
    assert position.question_id == transaction.question_id
    assert position.question_id == question.id
    assert position.user_id == transaction.user_id
    prices = question.outcome_probs
    price = prices[0] if transaction.answer else prices[1]
    insert_transaction(conn, transaction)
    new_position, budget_delta = get_new_position(position, transaction, price)
    update_position(conn, new_position)
    update_user_budget(conn, position.user_id, budget_delta)


def insert_transaction(conn: sqlite3.Connection, transaction: Transaction):
    cursor = conn.cursor()
    insert_transaction_query = load_sql_query("insert_transaction.sql")
    cursor.execute(
        insert_transaction_query,
        (
            transaction.user_id,
            transaction.question_id,
            transaction.transaction_type,
            transaction.answer,
            transaction.amount,
        ),
    )
    conn.commit()


def update_position(conn: sqlite3.Connection, position: Position):
    cursor = conn.cursor()
    update_position_query = load_sql_query("upsert_position.sql")
    cursor.execute(
        update_position_query,
        (
            position.user_id,
            position.question_id,
            position.stake_yes,
            position.stake_no,
            position.stake_yes,  # repetition for the case on conflict, trash syntax idk
            position.stake_no,
        ),
    )
    conn.commit()


def update_user_budget(conn: sqlite3.Connection, user_id: int, budget_delta: float):
    cursor = conn.cursor()
    update_user_budget_query = load_sql_query("update_user_budget.sql")
    cursor.execute(
        update_user_budget_query,
        (budget_delta, user_id),
    )
    conn.commit()


def resolve_updated_positions(
    conn: sqlite3.Connection,
    resolved_questions: list[Question],
):
    for resolved_question in resolved_questions:
        positions = get_positions_on_question(conn, resolved_question.id)
        for position in positions:
            if position.stake_yes > 0.0:
                sell_yes = Transaction(
                    user_id=position.user_id,
                    question_id=position.question_id,
                    answer=True,
                    transaction_type="sell",
                    amount=position.stake_yes * resolved_question.outcome_probs[0],
                )
                perform_transaction(conn, sell_yes, position, resolved_question)
            # the position in db was updated but perform_transaction needs position from the program too(might have to change that) so im updating it if a transaction was performed
            position = Position(
                user_id=position.user_id,
                question_id=position.question_id,
                stake_yes=0.0,
                stake_no=position.stake_no,
            )
            if position.stake_no > 0.0:
                sell_no = Transaction(
                    user_id=position.user_id,
                    question_id=position.question_id,
                    answer=False,
                    transaction_type="sell",
                    amount=position.stake_no * resolved_question.outcome_probs[1],
                )
                perform_transaction(conn, sell_no, position, resolved_question)

            remove_position(conn, position)


def remove_position(conn: sqlite3.Connection, position: Position):
    # Very careful when using because it removes a position from the db
    assert position.stake_yes == 0.0
    assert position.stake_no == 0.0
    cursor = conn.cursor()
    remove_position_query = load_sql_query("remove_position.sql")
    cursor.execute(remove_position_query, (position.user_id, position.question_id))
    conn.commit()
