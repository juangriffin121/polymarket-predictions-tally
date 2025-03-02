from polymarket_predictions_tally.initialization import initialize_config_if_needed

# from importlib.resources import files
#
# path = files("polymarket_predictions_tally.config").joinpath("config.toml")
# _config = toml.loads(path.read_text(encoding="utf-8"))
_config = initialize_config_if_needed()
MAX_TIME_DELTA_DAYS = _config["settings"]["max_time_delta_days"]
MAX_QUESTIONS = _config["settings"]["max_questions"]
