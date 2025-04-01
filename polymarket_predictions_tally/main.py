import sqlite3
from polymarket_predictions_tally.cli.command import cli
from polymarket_predictions_tally.initialization import DB_PATH, initialize_db_if_needed


def main():
    initialize_db_if_needed()
    with sqlite3.connect(DB_PATH) as conn:
        cli(obj={"conn": conn})  # Pass the connection here


if __name__ == "__main__":
    main()
