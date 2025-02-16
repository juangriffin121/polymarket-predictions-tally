import json
import sqlite3
from typing import List

from polymarket_predictions_tally.logic import (
    Event,
    InvalidResponse,
    Question,
    User,
    Response,
)


def load_sql_query(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def has_user_answered(
    conn: sqlite3.Connection, user_id: int, question_id: int
) -> Response | None:
    cursor = conn.cursor()
    query = load_sql_query("./database/has_user_answered.sql")
    cursor.execute(query, (user_id, question_id))
    results = cursor.fetchone()
    if results is not None:
        return Response(*results)


def remove_user(conn: sqlite3.Connection, id: int):
    cursor = conn.cursor()
    insert_user_query = load_sql_query("./database/remove_user.sql")
    cursor.execute(insert_user_query, (id,))
    conn.commit()


def update_user(conn: sqlite3.Connection, id: int, new_budget: int):
    cursor = conn.cursor()
    update_user_query = load_sql_query("./database/update_user.sql")
    cursor.execute(update_user_query, (new_budget, id))
    conn.commit()


def insert_user(conn: sqlite3.Connection, user: User):
    cursor = conn.cursor()
    insert_user_query = load_sql_query("./database/insert_user.sql")
    cursor.execute(insert_user_query, (user.id, user.username, user.budget))
    conn.commit()


def remove_event(conn: sqlite3.Connection, id: int):
    raise NotImplementedError


def insert_event(conn: sqlite3.Connection, event: Event):
    raise NotImplementedError


def is_question_in_db(conn: sqlite3.Connection, question_id) -> bool:
    query = load_sql_query("./database/is_question_in_db.sql")
    cursor = conn.cursor()
    cursor.execute(query, (question_id,))
    results = cursor.fetchone()
    return bool(results[0])


def insert_response(conn: sqlite3.Connection, response: Response):
    params = (
        response.user_id,
        response.question_id,
        response.answer,
        response.timestamp,
        response.correct,
        response.explanation,
    )
    insert_response_query = load_sql_query("./database/insert_response.sql")
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


def validate_response(
    conn: sqlite3.Connection, response: Response
) -> tuple[bool, bool]:
    user_ids = get_user_ids(conn)
    questions_ids = get_question_ids(conn)
    return (response.user_id in user_ids, response.question_id in questions_ids)


def get_user_ids(conn: sqlite3.Connection) -> List[int]:
    users_query = load_sql_query("./database/list_users_id.sql")
    cursor = conn.cursor()
    cursor.execute(users_query)
    results = cursor.fetchall()
    return [row[0] for row in results]


def get_question_ids(conn: sqlite3.Connection) -> List[int]:
    questions_query = load_sql_query("./database/list_questions_id.sql")
    cursor = conn.cursor()
    cursor.execute(questions_query)
    results = cursor.fetchall()
    return [row[0] for row in results]


def update_question(conn: sqlite3.Connection, question: Question):
    remove_question(conn, question.id)
    insert_question(conn, question)


def update_present_questions(conn: sqlite3.Connection, api_questions: List[Question]):
    for question in api_questions:
        if is_question_in_db(conn, question.id):
            update_question(conn, question)


def remove_question(conn: sqlite3.Connection, id: int):
    remove_question_query = load_sql_query("./database/remove_question.sql")
    cursor = conn.cursor()
    cursor.execute(remove_question_query, (id,))
    conn.commit()


def insert_question(conn: sqlite3.Connection, question: Question):
    # Convert lists to JSON strings
    outcome_probs_json = json.dumps(question.outcome_probs)
    outcomes_json = json.dumps(question.outcomes)

    insert_question_query = load_sql_query("./database/insert_question.sql")
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
