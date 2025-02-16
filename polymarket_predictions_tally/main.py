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
    user = User(id=1, username="griffin", budget=100)

    question = Question(
        id=2,
        question="Will Julius Caesar win the 100 BC roman dictatorial election?",
        outcome_probs=[90.0, 10.0],
        outcomes=["Yes", "No"],
        end_date=datetime(100, 10, 10),
        outcome=None,
        description="",
        tag="Politics",
    )
    response = get_response(user, question)
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
    main3()
