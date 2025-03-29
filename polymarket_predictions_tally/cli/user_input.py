from datetime import datetime
from typing import List, Optional

import click

from polymarket_predictions_tally.logic import (
    Position,
    Question,
    Response,
    Transaction,
    User,
)


def process_prediction(
    user: User,
    api_questions: list[Question],
    previous_user_responses: list[Optional[Response]],
) -> tuple[Question, Optional[Response]]:
    [chosen_question, previous_user_response] = prompt_question_selection(
        api_questions, previous_user_responses, "predict"
    )
    return prompt_for_response(user, chosen_question, previous_user_response)


def prompt_question_selection(
    questions: List[Question], responses: list[Optional[Response]], mode: str
) -> tuple[Question, Optional[Response]]:
    options = []
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        status = f"[{response.answer}]" if response else ""
        options.append(
            f"{i}. {question.question} [{question.end_date.date()}] {status}".strip()
        )

    # Prompt the user to select a question
    click.echo("\nAvailable Questions:\n" + "\n".join(options))

    choice = click.prompt(
        "Select a question by number", type=click.IntRange(1, len(questions))
    )

    # Return the selected question and its associated response
    return questions[choice - 1], responses[choice - 1]


def prompt_for_response(
    user: User, question: Question, previous_response: Optional[Response]
) -> tuple[Question, Optional[Response]]:
    """
    Prompts the user for an answer to the given question.

    If previous_response is provided, the prompt should show:
       "You answered [answer] to <question text>.
        Do you want to change your answer? [yes/no]"
    If the user chooses not to change their answer, return None.
    Otherwise, prompt the user to provide a new answer (e.g. "yes" or "no") and return it.
    """
    click.echo(f"{question.question} {question.end_date}")
    if previous_response is not None:
        click.echo(f"You answered [{previous_response.answer}] before")
        click.echo(f"Your explanation for it was:\n\t{previous_response.explanation}")
        if click.confirm("Do you wish to change anything about your previous answer?"):
            return question, get_response(user, question)
        else:
            return question, None
    return question, get_response(user, question)


def get_response(user: User, question: Question) -> Response:
    if click.confirm(question.question):
        answer = "Yes"
    else:
        answer = "No"

    if click.confirm("Do you wish to give an explanation for your choice?"):
        explanation = click.edit("")
        if explanation == "":
            explanation = None
    else:
        explanation = None

    return Response(
        user_id=user.id,
        question_id=question.id,
        answer=answer,
        timestamp=datetime.now(),
        correct=None,
        explanation=explanation,
    )


# Betting input

# making this dry was seemed like quite a mess for the problem and there are only going to be two interactions from the user with questions i think, betting and predicting


def process_bet(
    user: User,
    api_questions: list[Question],
    user_positions: list[Optional[Position]],
) -> tuple[Question, Optional[Transaction], Optional[Position]]:
    [chosen_question, user_position] = prompt_question_selection_for_bet(
        api_questions, user_positions
    )
    return prompt_for_transaction(user, chosen_question, user_position)


def prompt_question_selection_for_bet(
    questions: List[Question], positions: list[Optional[Position]]
) -> tuple[Question, Optional[Position]]:
    options = []
    for i, (question, position) in enumerate(zip(questions, positions), 1):
        status = (
            f"[Yes: {position.stake_yes}$] [No: {position.stake_no}$]"
            if position
            else ""
        )
        options.append(
            f"{i}.\t{question.question} [{question.end_date.date()}] {status}".strip()
        )

    # Prompt the user to select a question
    click.echo("\nAvailable Questions:\n" + "\n".join(options))

    choice = click.prompt(
        "Select a question by number", type=click.IntRange(1, len(questions))
    )

    return questions[choice - 1], positions[choice - 1]


def prompt_for_transaction(
    user: User, question: Question, user_position: Optional[Position]
) -> tuple[Question, Optional[Transaction], Optional[Position]]:
    click.echo(f"{question.question} {question.end_date}")
    return question, get_transaction(user, question, user_position), user_position


def get_transaction(
    user: User, question: Question, position: Optional[Position]
) -> Optional[Transaction]:
    answer = click.confirm(question.question)
    prices = question.outcome_probs
    price = prices[0] if answer else prices[1]
    if position is not None:
        stake = position.stake_yes if answer else position.stake_no
        if stake == 0.0:
            click.echo(
                "You don't have any stake to sell for this answer; defaulting to a buy."
            )
            transaction_type = "buy"
            max_amount = user.budget
        else:
            transaction_type = click.prompt(
                f"Select transaction type\nYou can sell up to {stake * price} and buy up to {user.budget}",
                type=click.Choice(["buy", "sell"], case_sensitive=False),
            )

        if transaction_type == "buy":
            max_amount = user.budget
        elif transaction_type == "sell":
            max_amount = stake * price
        else:
            raise ValueError(
                "Invalid transaction type, click should prevent this, debug time"
            )

        amount = get_amount(max_amount)
        if amount is None:
            return None

    else:
        click.echo("No existing position found. Only buying is available.")
        transaction_type = "buy"
        max_amount = user.budget
        amount = get_amount(max_amount)
        if amount is None:
            return None

    return Transaction(
        user_id=user.id,
        question_id=question.id,
        transaction_type=transaction_type,
        answer=answer,
        amount=amount,
    )


# Change to loop to avoid stack overflow
def get_amount(max_amount: float) -> Optional[float]:
    while True:
        amount = click.prompt(
            f"Enter amount. limit {max_amount}$",
            type=float,
        )
        if 0 < amount <= max_amount:
            return amount
        else:
            click.echo("Invalid amount. Must be within the allowed range.")
            if click.confirm(f"Do you wish to try again?"):
                continue
            else:
                return None
