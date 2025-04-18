import sqlite3
from polymarket_predictions_tally.database.utils import load_sql_query, newest_response
from polymarket_predictions_tally.logic import Position, Question, Response, User


def get_user(conn: sqlite3.Connection, username: str) -> User | None:
    cursor = conn.cursor()
    query = load_sql_query("get_user.sql")
    cursor.execute(query, (username,))
    results = cursor.fetchone()
    if results is not None:
        return User(*results)


def get_all_users(conn: sqlite3.Connection) -> list[User]:
    cursor = conn.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)
    results = cursor.fetchall()
    return [User(*result) for result in results]


def get_user_from_id(conn: sqlite3.Connection, user_id: int) -> User | None:
    cursor = conn.cursor()
    query = load_sql_query("get_user_from_id.sql")
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()
    if results is not None:
        return User(*results)


def has_user_answered(
    conn: sqlite3.Connection, user_id: int, question_id: int
) -> Response | None:
    cursor = conn.cursor()
    query = load_sql_query("has_user_answered.sql")
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
    query = load_sql_query("is_question_in_db.sql")
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
    users_query = load_sql_query("list_users_id.sql")
    cursor = conn.cursor()
    cursor.execute(users_query)
    results = cursor.fetchall()
    return [row[0] for row in results]


def get_question_ids(conn: sqlite3.Connection) -> list[int]:
    questions_query = load_sql_query("list_questions_id.sql")
    cursor = conn.cursor()
    cursor.execute(questions_query)
    results = cursor.fetchall()
    return [row[0] for row in results]


def get_active_question_ids(conn: sqlite3.Connection) -> list[int]:
    questions_query = load_sql_query("list_active_questions.sql")
    cursor = conn.cursor()
    cursor.execute(questions_query)
    results = cursor.fetchall()
    return [row[0] for row in results]


def get_all_responses_to_questions(
    conn: sqlite3.Connection, questions: list[Question]
) -> list[list[Response]]:
    cursor = conn.cursor()
    responses = []
    for question in questions:
        query = load_sql_query("get_responses_to_question.sql")
        cursor.execute(query, (question.id,))
        results = cursor.fetchall()
        responses_to_question = [
            Response.from_database_entry(result) for result in results
        ]
        responses.append(responses_to_question)

    return responses


def get_latest_responses_to_questions(
    conn: sqlite3.Connection, questions: list[Question]
) -> list[dict[int, Response]]:
    cursor = conn.cursor()
    responses = []
    for question in questions:
        query = load_sql_query("get_responses_to_question.sql")
        cursor.execute(query, (question.id,))
        results = cursor.fetchall()
        responses_to_question = [
            Response.from_database_entry(result) for result in results
        ]
        responses_to_question_dict = {}
        for response in responses_to_question:
            responses_to_question_dict.setdefault(response.user_id, []).append(response)
        latest_responses_to_question = {
            user_id: newest_response(responses_to_question_by_user)
            for user_id, responses_to_question_by_user in responses_to_question_dict.items()
        }

        responses.append(latest_responses_to_question)

    return responses


def get_users_affected_by_update(
    conn: sqlite3.Connection,
    latest_responses: list[dict[int, Response]],
    updated_questions: list[Question],
) -> dict[User, list[tuple[Response, bool]]]:
    info = []
    info_dict = {}
    for responses_to_question, question in zip(latest_responses, updated_questions):
        for user_id, latest_response in responses_to_question.items():
            user = get_user_from_id(conn, user_id)
            user_answer = latest_response.answer
            assert not question.outcome is None
            if question.outcome == True:
                correct_answer = "Yes"
            else:
                correct_answer = "No"
            user_is_right = user_answer == correct_answer
            info.append((user, latest_response, user_is_right))
            info_dict.setdefault(user, []).append((latest_response, user_is_right))
            assert user_answer in ("Yes", "No")

    return info_dict


def get_user_id_by_name(conn: sqlite3.Connection, username: str) -> int | None:
    cursor = conn.cursor()
    query = load_sql_query("get_user_id_by_username.sql")
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    assert len(results) <= 1
    if len(results) == 1:
        return results[0][0]


def get_all_responses(conn: sqlite3.Connection, user_id: int) -> list[Response]:
    cursor = conn.cursor()
    query = load_sql_query("get_all_responses.sql")
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    return [Response.from_database_entry(result) for result in results]


def get_latest_responses(conn: sqlite3.Connection, user_id: int) -> list[Response]:
    all_responses = get_all_responses(conn, user_id)
    responses_dict = {}
    for response in all_responses:
        responses_dict.setdefault(response.question_id, []).append(response)
    return [
        newest_response(responses) for question_id, responses in responses_dict.items()
    ]


def get_responses(
    conn: sqlite3.Connection, user_id: int, all: bool = False
) -> list[Response]:
    if all:
        return get_all_responses(conn, user_id)
    else:
        return get_latest_responses(conn, user_id)


def get_question_from_id(conn: sqlite3.Connection, question_id: int) -> Question:
    cursor = conn.cursor()
    query = load_sql_query("get_question_from_id.sql")
    cursor.execute(query, (question_id,))
    results = cursor.fetchone()
    return Question.from_database_entry(results)


def get_questions_from_ids(conn: sqlite3.Connection, ids: list[int]) -> list[Question]:
    questions = []
    for question_id in ids:
        questions.append(get_question_from_id(conn, question_id))

    return questions


def get_stats(conn: sqlite3.Connection, user_id: int) -> tuple[int, int]:
    cursor = conn.cursor()
    query = load_sql_query("get_stats.sql")
    cursor.execute(query, (user_id,))
    return cursor.fetchone()


def get_user_positions(
    conn: sqlite3.Connection,
    api_questions: list[Question],
    user_id: int,
) -> list[Position | None]:
    previous_user_responses = []
    for question in api_questions:
        response = get_user_position(conn, user_id, question.id)
        previous_user_responses.append(response)
    return previous_user_responses


def get_user_position(
    conn: sqlite3.Connection, user_id: int, question_id: int
) -> Position | None:
    cursor = conn.cursor()
    query = load_sql_query("get_user_position.sql")
    cursor.execute(query, (user_id, question_id))
    results = cursor.fetchone()
    if results is not None:
        return Position(*results)


def get_updated_positions(
    conn: sqlite3.Connection, updated_questions: list[Question | None]
) -> dict[int, list[Position]]:
    positions_by_user = {}
    for question in updated_questions:
        if question:
            positions = get_positions_on_question(conn, question.id)
            for position in positions:
                positions_by_user.setdefault(position.user_id, []).append(position)
    return positions_by_user


def get_positions_on_question(
    conn: sqlite3.Connection, question_id: int
) -> list[Position]:
    cursor = conn.cursor()
    query = load_sql_query("get_positions_on_question.sql")
    cursor.execute(query, (question_id,))
    results = cursor.fetchall()
    positions = []
    for result in results:
        positions.append(Position(*result))
    return positions


def get_all_user_positions(conn: sqlite3.Connection, user_id: int) -> list[Position]:
    cursor = conn.cursor()
    query = load_sql_query("get_all_user_positions.sql")
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    positions = []
    for result in results:
        positions.append(Position(*result))
    return positions


def get_questions_from_positions(
    conn: sqlite3.Connection, positions: list[Position]
) -> list[Question]:
    questions = [
        get_question_from_id(conn, position.question_id) for position in positions
    ]
    assert all(question is not None for question in questions)
    return questions
