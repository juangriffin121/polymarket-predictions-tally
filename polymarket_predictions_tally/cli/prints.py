from click.utils import echo
from polymarket_predictions_tally.logic import Question, Response, User
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
        print(question.outcome)
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

        click.echo(f"\t{question.question} {color}[{response.answer}]{reset}")

    click.echo("")
    click.echo(f"User: [{user.username}]")
    click.echo(f"Stats: {green}{stats[0]}[+]{reset} {red}{stats[1]}[-]{reset}")
