from platformdirs import user_config_dir, user_data_dir
import pathlib
import sqlite3
from polymarket_predictions_tally.database.utils import load_sql_query
import toml
from importlib.resources import open_text

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


def initialize_config_if_needed():
    config_dir = pathlib.Path(user_config_dir(APP_NAME))
    config_file = config_dir / "config.toml"

    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        with open_text(
            "polymarket_predictions_tally.config", "config.toml", encoding="utf-8"
        ) as f:
            default_config = f.read()
        config_file.write_text(default_config, encoding="utf-8")

    config = toml.loads(config_file.read_text(encoding="utf-8"))
    return config
