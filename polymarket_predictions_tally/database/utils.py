from polymarket_predictions_tally.logic import Response


def newest_response(responses: list[Response]) -> Response:
    return max(responses, key=lambda response: response.timestamp)


def load_sql_query(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()
