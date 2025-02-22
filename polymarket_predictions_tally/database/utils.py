from polymarket_predictions_tally.logic import Response
from importlib.resources import files


def newest_response(responses: list[Response]) -> Response:
    return max(responses, key=lambda response: response.timestamp)


# def load_sql_query(file_path: str) -> str:
#     with open(file_path, "r") as f:
#         return f.read()


def load_sql_query(filename: str) -> str:
    path = files("polymarket_predictions_tally.queries").joinpath(filename)
    return path.read_text(encoding="utf-8")
