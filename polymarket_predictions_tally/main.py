# Example usage:
from datetime import datetime
import sqlite3
from polymarket_predictions_tally.api import (
    get_events,
    get_question_raw,
    get_questions,
)
from polymarket_predictions_tally.cli import get_response
from polymarket_predictions_tally.database import insert_question, load_sql_query
from polymarket_predictions_tally.logic import Question, Response, User
from polymarket_predictions_tally.utils import indent_lines
from tests.cli.test_get_response import get_response_cmd
from tests.cli.test_prompt_question_selection import select_question_cmd


def clear(conn: sqlite3.Connection):
    cursor = conn.cursor()
    clear_queries = [
        "DELETE FROM users",
        "DELETE FROM questions;",
        "DELETE FROM responses;",
        "DELETE FROM transactions;",
        "DELETE FROM positions;",
        "DELETE FROM sqlite_sequence WHERE name IN ('questions', 'responses', 'users', 'transactions', 'positions');",
    ]

    for query in clear_queries:
        cursor.execute(query)
    conn.commit()


def main3():
    response = get_response_cmd()
    print(response)


def main4():
    response = select_question_cmd()
    print(response)


def main():
    with sqlite3.connect("./database/database.db") as conn:
        clear(conn)
        questions = get_questions(tag="Politics", limit=3)
        for question in questions:
            print(question)
            insert_question(conn, question)


def main2():
    events = get_events("Politics")
    for event in events:
        print(event)
        for question in event.questions:
            print(indent_lines(str(question)))

    print("getting question 253727")
    __import__("pprint").pprint(get_question_raw(id=253727))


if __name__ == "__main__":
    main4()
