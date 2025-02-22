from platformdirs import user_data_dir
import pathlib
import sqlite3
from polymarket_predictions_tally.database.utils import load_sql_query

APP_NAME = "polymarket-predictions-tally"
data_dir = pathlib.Path(user_data_dir(APP_NAME))
DB_PATH = data_dir / "database.db"

# Ensure the directory exists
data_dir.mkdir(parents=True, exist_ok=True)


def initialize_db_if_needed():
    # If the database file doesn't exist, create it and run the initialization script
    if not DB_PATH.exists():
        # Ensure the directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Connect to (or create) the database
        conn = sqlite3.connect(str(DB_PATH))
        try:
            sql_script = load_sql_query("setup.sql")
            conn.executescript(sql_script)
            conn.commit()
        finally:
            conn.close()
