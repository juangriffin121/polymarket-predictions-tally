# Example usage:
import sqlite3
from polymarket_predictions_tally.api import (
    get_events,
    get_question_raw,
    get_questions,
)
from polymarket_predictions_tally.database import insert_question
from polymarket_predictions_tally.utils import indent_lines


def main():
    with sqlite3.connect("./database/database.db") as conn:
        questions = get_questions(tag="Politics", limit=3)
        for question in questions:
            insert_question(conn, question)
            print(question)


def main2():
    events = get_events("Politics")
    for event in events:
        print(event)
        for question in event.questions:
            print(indent_lines(str(question)))

    print("getting question 253727")
    __import__("pprint").pprint(get_question_raw(id=253727))


if __name__ == "__main__":
    main()
