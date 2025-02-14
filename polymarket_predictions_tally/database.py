import json
import sqlite3

from polymarket_predictions_tally.logic import Event, Question, User


# Function to load an SQL query from a file
def load_sql_query(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def remove_user(conn: sqlite3.Connection, id: int):
    cursor = conn.cursor()
    insert_user_query = load_sql_query("./database/remove_user.sql")
    cursor.execute(insert_user_query, (id,))


def insert_user(conn: sqlite3.Connection, user: User):
    cursor = conn.cursor()
    insert_user_query = load_sql_query("./database/insert_user.sql")
    cursor.execute(insert_user_query, (user.id, user.username, user.budget))


def remove_event(conn: sqlite3.Connection, id: int):
    raise NotImplementedError


def insert_event(conn: sqlite3.Connection, event: Event):
    raise NotImplementedError


def update_question(conn: sqlite3.Connection, question: Question):
    remove_question(conn, question.id)
    insert_question(conn, question)


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
