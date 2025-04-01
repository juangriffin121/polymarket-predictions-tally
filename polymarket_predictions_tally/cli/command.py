import sqlite3
from sys import call_tracing
import click
from click.utils import echo

from polymarket_predictions_tally import integration
from polymarket_predictions_tally.integration import (
    run_user_session,
    show_users,
    update_database,
)


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    pass


@cli.command()  # of group cli
@click.argument("username")
@click.pass_context
def predict(ctx, username):
    conn = ctx.obj["conn"]
    run_user_session(username, conn)


@cli.command()  # of group cli
@click.pass_context
def update(ctx):
    echo("Updating database")
    conn = ctx.obj["conn"]
    update_database(conn)


@cli.command()  # of group cli
@click.argument("username")
@click.pass_context
def history(ctx, username):
    conn = ctx.obj["conn"]
    integration.history(username, conn)


@cli.command()  # of group cli
@click.pass_context
def users(ctx):
    conn = ctx.obj["conn"]
    show_users(conn)


@cli.command()  # of group cli
@click.argument("username")
@click.pass_context
def bet(ctx, username):
    conn = ctx.obj["conn"]
    integration.bet(username, conn)
