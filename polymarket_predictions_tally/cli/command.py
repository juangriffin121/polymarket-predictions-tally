import click


@click.group
def cli():
    pass


@cli.command  # of group cli
@click.argument("username")
def predict(username):
    raise NotImplementedError
