from datetime import datetime
from typing import List, Optional

import click

from polymarket_predictions_tally.cli.prints import draw_bar
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
    max_len = max([len(q.question) for q in questions])

    for i, (question, response) in enumerate(zip(questions, responses), 1):
        status = f"[{response.answer[0]}]" if response else "   "
        options.append(
            f"| {i} \t| {question.end_date.date()} \t| {status} | {question.question}{' '*(max_len - len(question.question))} |".strip()
        )

    # Prompt the user to select a question

    click.echo(f"\n| Nr \t| EndDate\t| Ans | Question{' '*(max_len - 8)} |")
    bars = f"|-------|---------------|-----|---------{'-'*(max_len - 8)}-|"
    click.echo(bars)
    click.echo("\n".join(options))

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
    max_len = max([len(q.question) for q in questions])
    percentage_bar_len = 10
    for i, (position, question) in enumerate(zip(positions, questions), 1):
        stake_yes = str(round(position.stake_yes, 1)) if position else ""
        stake_yes = f"{stake_yes}{' '*(10 - len(stake_yes))}"
        stake_no = str(round(position.stake_no, 1)) if position else ""
        stake_no = f"{stake_no}{' '*(10 - len(stake_no))}"
        options.append(
            f"| {i} \t| {question.end_date.date()} \t| {question.question}{' '*(max_len - len(question.question))} | {stake_yes} | {draw_bar(question.outcome_probs[0], percentage_bar_len)} | {stake_no}|".strip()
        )

    click.echo(
        f"\n| Nr \t| EndDate\t| Question{' '*(max_len - 8)} | StakeYes\t | Prices(Yes/No){' '*(percentage_bar_len + 10 - 14)}| StakeNo   |"
    )
    bars = f"|-------|---------------|---------{'-'*(max_len - 8)}-|------------|{'-'*(percentage_bar_len + 10 +1)}|-----------|"
    click.echo(bars)
    click.echo("\n".join(options), color=True)

    choice = click.prompt(
        "Select a question by number", type=click.IntRange(1, len(positions))
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


def prompt_sell(
    user: User, positions: list[Position], questions: list[Question]
) -> tuple[Transaction | None, Position, Question]:
    position, question = choose_position(positions, questions)
    transaction = get_transaction(user, question, position)
    return transaction, position, question


def choose_position(
    positions: list[Position], questions: list[Question]
) -> tuple[Position, Question]:
    options = []
    max_len = max([len(q.question) for q in questions])
    percentage_bar_len = 10
    for i, (position, question) in enumerate(zip(positions, questions), 1):
        stake_yes = str(round(position.stake_yes, 1))
        stake_yes = f"{stake_yes}{' '*(10 - len(stake_yes))}"
        stake_no = str(round(position.stake_no, 1))
        stake_no = f"{stake_no}{' '*(10 - len(stake_no))}"
        options.append(
            f"| {i} \t| {question.end_date.date()} \t| {question.question}{' '*(max_len - len(question.question))} | {stake_yes} | {draw_bar(question.outcome_probs[0], percentage_bar_len)} | {stake_no} |".strip()
        )

    click.echo(
        f"\n| Nr \t| EndDate\t| Question{' '*(max_len - 8)} | StakeYes   | Prices(Yes/No){' '*(percentage_bar_len + 10 -14)}| StakeNo    |"
    )
    bars = f"|-------|---------------|---------{'-'*(max_len - 8)}-|------------|{'-'*(percentage_bar_len + 11)}|------------|"
    click.echo(bars)
    click.echo("\n".join(options), color=True)

    choice = click.prompt(
        "Select a position by number", type=click.IntRange(1, len(positions))
    )
    return positions[choice - 1], questions[choice - 1]
