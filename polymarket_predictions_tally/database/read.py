import sqlite3
from polymarket_predictions_tally.logic import Question, Response, User
from polymarket_predictions_tally.utils import load_sql_query


def get_user(conn: sqlite3.Connection, username: str) -> User | None:
    cursor = conn.cursor()
    query = load_sql_query("./database/get_user.sql")
    cursor.execute(query, (username,))
    results = cursor.fetchone()
    if results is not None:
        return User(*results)


def has_user_answered(
    conn: sqlite3.Connection, user_id: int, question_id: int
) -> Response | None:
    cursor = conn.cursor()
    query = load_sql_query("./database/has_user_answered.sql")
    cursor.execute(query, (user_id, question_id))
    results = cursor.fetchone()
    if results is not None:
        return Response(*results)


def get_previous_user_responses(
    conn: sqlite3.Connection,
    api_questions: list[Question],
    user_id: int,
) -> list[Response | None]:
    previous_user_responses = []
    for question in api_questions:
        response = has_user_answered(conn, user_id, question.id)
        previous_user_responses.append(response)
    return previous_user_responses


def is_question_in_db(conn: sqlite3.Connection, question_id) -> bool:
    query = load_sql_query("./database/is_question_in_db.sql")
    cursor = conn.cursor()
    cursor.execute(query, (question_id,))
    results = cursor.fetchone()
    return bool(results[0])


def validate_response(
    conn: sqlite3.Connection, response: Response
) -> tuple[bool, bool]:
    user_ids = get_user_ids(conn)
    questions_ids = get_question_ids(conn)
    return (response.user_id in user_ids, response.question_id in questions_ids)


def get_user_ids(conn: sqlite3.Connection) -> list[int]:
    users_query = load_sql_query("./database/list_users_id.sql")
    cursor = conn.cursor()
    cursor.execute(users_query)
    results = cursor.fetchall()
    return [row[0] for row in results]


def get_question_ids(conn: sqlite3.Connection) -> list[int]:
    questions_query = load_sql_query("./database/list_questions_id.sql")
    cursor = conn.cursor()
    cursor.execute(questions_query)
    results = cursor.fetchall()
    return [row[0] for row in results]
