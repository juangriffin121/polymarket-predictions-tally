import sqlite3
from polymarket_predictions_tally.api import (
    get_questions,
    get_questions_by_id_list,
)
from polymarket_predictions_tally.cli.command import cli
from polymarket_predictions_tally.database.write import insert_question


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


def main():
    with sqlite3.connect("./database/database.db") as conn:
        clear(conn)
        questions = get_questions(tag="Politics", limit=3)
        for question in questions:
            print(question)
            insert_question(conn, question)


if __name__ == "__main__":
    cli()
