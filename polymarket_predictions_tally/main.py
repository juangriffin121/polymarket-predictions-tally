# Example usage:
from polymarket_predictions_tally.api import get_events, get_question, get_questions
from polymarket_predictions_tally.utils import indent_lines


if __name__ == "__main__":
    questions = get_questions(tag="Politics")
    for question in questions:
        print(question)
    # events = get_events("Politics")
    # for event in events:
    #     print(event)
    #     for question in event.questions:
    #         print(indent_lines(str(question)))

    # print("getting question 512337")
    # print(get_question(id=512337))
