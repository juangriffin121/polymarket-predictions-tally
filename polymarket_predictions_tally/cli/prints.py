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
    for user_id, positions in updated_positions.items():
        username = users[user_id].username
        click.echo(username)
        net_profit = 0.0
        for position in positions:
            # can fail in getting question by id
            new_question = updated_questions_dict[position.question_id]
            old_question = old_questions_dict[position.question_id]
            delta_yes = new_question.outcome_probs[0] - old_question.outcome_probs[0]
            delta_no = new_question.outcome_probs[1] - old_question.outcome_probs[1]
            profit = delta_yes * position.stake_yes + delta_no * position.stake_no
            status = "Sold" if position.question_id in resolved_question_ids else ""
            click.echo(
                f"Question: {new_question.question} StakeYes: {position.stake_yes} DeltaYes: {round(delta_yes, 2)} StakeNo: {position.stake_no} DeltaNo: {round(delta_no,4)} Profit: {round(profit,4)} {status}"
            )
            net_profit += profit
        click.echo(f"NetProfit: {round(net_profit,2)}")


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

    bar = f"{green}{percent_yes}% {'█' * cells_yes}{red}{'█' * cells_no} {percent_no}%{reset}"
    return bar
