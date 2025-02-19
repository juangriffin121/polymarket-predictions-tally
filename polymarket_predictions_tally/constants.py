import toml

_config = toml.load("config.toml")
MAX_TIME_DELTA_DAYS = _config["settings"]["max_time_delta_days"]
MAX_QUESTIONS = _config["settings"]["max_questions"]
