import click
from click.utils import echo

from polymarket_predictions_tally.integration import run_user_session, update_database


@click.group()
def cli():
    pass


@cli.command()  # of group cli
@click.argument("username")
def predict(username):
    click.echo("enters")
    run_user_session(username)


@cli.command()  # of group cli
def update():
    echo("Updating database")
    update_database()
