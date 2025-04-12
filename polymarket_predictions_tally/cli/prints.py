from types import new_class
from click.utils import echo
from polymarket_predictions_tally.logic import Position, Question, Response, User
import click


def inform_users_of_change(
    update_info: dict[User, list[tuple[Response, bool]]],
    updated_questions: list[Question],
):
    if updated_questions == []:
        click.echo("Everything up to date")
    updated_questions_dict = {question.id: question for question in updated_questions}
    for user, response_info in update_info.items():
        right_count = sum([correct for response, correct in response_info])
        wrong_count = len(response_info) - right_count
        click.echo(
            f"User {user.username} had {right_count} right and {wrong_count} wrong"
        )
        click.echo("Detailed description:")
        for response, correct in response_info:
            question = updated_questions_dict[response.question_id]
            color = (
                "\033[92m" if correct else "\033[91m"
            )  # Green for correct, Red for wrong
            reset = "\033[0m"
            click.echo(
                f"\tQuestion: {question.question} {color}[{response.answer}]{reset}"
            )

    inform_stats_update()


def inform_users_of_stocks_change(
    users: dict[int, User],
    updated_positions: dict[int, list[Position]],
    updated_questions: list[Question | None],
    old_questions: list[Question],
    resolved_questions: list[Question],
):
    updated_questions_dict = {
        question.id: question for question in updated_questions if question is not None
    }
    old_questions_dict = {question.id: question for question in old_questions}
    resolved_question_ids = {question.id for question in resolved_questions}

    bar_length = 10
    max_len = max([len(q.question) for q in old_questions])
    for user_id, positions in updated_positions.items():
        username = users[user_id].username
        click.echo(username)
        net_profit = 0.0
        changes_whitespace = " " * (bar_length - len("NewPrices") + 8)
        changes_line = "-" * (bar_length + 11)

        click.echo(
            f"| Question{' '*(max_len - len('Question'))} | StakeYes   | DeltaYes | NewPrices {changes_whitespace} | DeltaNo | StakeNo    | Profit         | Status\t |"
        )
        click.echo(
            f"|{'-'*(max_len+2)}|------------|----------|{changes_line}|---------|------------|----------------|---------------|"
        )
        for position in positions:
            # can fail in getting question by id
            new_question = updated_questions_dict[position.question_id]
            old_question = old_questions_dict[position.question_id]
            delta_yes = new_question.outcome_probs[0] - old_question.outcome_probs[0]
            delta_no = new_question.outcome_probs[1] - old_question.outcome_probs[1]
            profit = delta_yes * position.stake_yes + delta_no * position.stake_no
            delta_yes_str = print_delta(delta_yes)
            delta_no_str = print_delta(delta_no)
            stake_yes = str(round(position.stake_yes, 1))
            stake_yes = f"{stake_yes}{' '*(10 - len(stake_yes))}"
            stake_no = str(round(position.stake_no, 1))
            stake_no = f"{stake_no}{' '*(10 - len(stake_no))}"
            status = (
                "Sold " if position.question_id in resolved_question_ids else "Active"
            )
            click.echo(
                f"| {new_question.question}{' '*(max_len - len(new_question.question))} | {stake_yes} | {delta_yes_str}{' '*(len('DeltaYes') - 3)} | {draw_bar(new_question.outcome_probs[0], bar_length)} | {delta_no_str}{' '*(len('DeltaNo') - 3)} | {stake_no} | {print_profit(profit)}\t | {status}\t |",
                color=True,
            )
            net_profit += profit
        click.echo(f"\nNetProfit: {print_profit(net_profit)}", color=True)


def print_delta(delta: float):
    sign = "+" if delta > 0 else "-"
    return f"{sign}{abs(round(delta*100))}%"


def print_profit(profit):
    sign = "+" if profit > 0 else (" " if profit == 0.0 else "-")
    arrow = "" if profit > 0 else (" " if profit == 0.0 else "")
    color = (
        "\033[32m" if profit > 0 else ("" if profit == 0.0 else "\033[31m")
    )  # green / red
    reset = "\033[0m"
    profit = f"{abs(round(profit, 1))}"
    profit = f"{profit}{' '*(5 - len(profit))}"
    return f"{color}{sign}{profit}{arrow}{reset}"


def inform_stats_update():
    pass


def user_not_in_db(username: str):
    click.echo(f" User {username} not in database, please try again")


def history(
    user: User,
    responses: list[Response],
    questions: list[Question],
    stats: tuple[int, int],
):
    red = "\033[91m"
    green = "\033[92m"
    reset = "\033[0m"

    click.echo(f"User [{user.username}]")
    click.echo("Responses:")
    for question, response in zip(questions, responses):
        match question.outcome:
            case None:
                correct = None
            case True | 1:
                correct = response.answer == "Yes"
            case False | 0:
                correct = response.answer == "No"

        match correct:
            case True:
                color = green
            case False:
                color = red
            case None:
                color = reset

        click.echo(
            f"\t[{question.id}] [{question.end_date}] {question.question} {color}[{response.answer}]{reset}"
        )

    click.echo("")
    click.echo(f"User: [{user.username}]")
    click.echo(f"Stats: {green}{stats[0]}[+]{reset} {red}{stats[1]}[-]{reset}")


def users(users_list: list[User]):
    for user in users_list:
        click.echo(f"{user.username}")


def draw_bar(prob_yes, bar_length=20):
    percent_yes = int(prob_yes * 100)
    percent_no = 100 - percent_yes

    cells_yes = int(prob_yes * bar_length)
    cells_no = bar_length - cells_yes

    red = "\033[91m"
    green = "\033[92m"
    reset = "\033[0m"
    pad_yes = " " * (3 - len(str(percent_yes)))
    pad_no = " " * (3 - len(str(percent_no)))

    bar = f"{green}{percent_yes}%{pad_yes}{'█' * cells_yes}{red}{'█' * cells_no} {percent_no}%{pad_no}{reset}"
    return bar
