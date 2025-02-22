from polymarket_predictions_tally.cli.command import cli
from polymarket_predictions_tally.initialization import initialize_db_if_needed


def main():
    initialize_db_if_needed()
    cli()


if __name__ == "__main__":
    main()
