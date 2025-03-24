import click
from click.utils import echo

from polymarket_predictions_tally import integration
from polymarket_predictions_tally.integration import (
    run_user_session,
    show_users,
    update_database,
)


@click.group()
def cli():
    pass


@cli.command()  # of group cli
@click.argument("username")
def predict(username):
    run_user_session(username)


@cli.command()  # of group cli
def update():
    echo("Updating database")
    update_database()


@cli.command()  # of group cli
@click.argument("username")
def history(username):
    integration.history(username)


@cli.command()  # of group cli
def users():
    show_users()


@cli.command()  # of group cli
@click.argument("username")
def bet(username):
    integration.bet(username)
