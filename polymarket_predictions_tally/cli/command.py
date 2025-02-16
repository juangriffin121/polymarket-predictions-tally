import click

from polymarket_predictions_tally.integration import run_user_session


@click.group()
def cli():
    click.echo("enters")
    pass


@cli.command()  # of group cli
@click.argument("username")
def predict(username):
    click.echo("enters")
    run_user_session(username)


if __name__ == "__main__":
    cli()
