from click.decorators import T
from polymarket_predictions_tally.logic import Position, Response, Transaction
from importlib.resources import files


def newest_response(responses: list[Response]) -> Response:
    return max(responses, key=lambda response: response.timestamp)


def load_sql_query(filename: str) -> str:
    path = files("polymarket_predictions_tally.queries").joinpath(filename)
    return path.read_text(encoding="utf-8")


def get_new_position(
    old_position: Position, transaction: Transaction, price: float
) -> tuple[Position, float]:
    assert transaction.transaction_type in {"buy", "sell"}
    buy = transaction.transaction_type == "buy"
    sign = 1 if buy else -1
    if transaction.answer is True:
        new_stake = old_position.stake_yes + sign * transaction.amount / price
        assert new_stake > 0
        return (
            Position(
                user_id=old_position.user_id,
                question_id=old_position.question_id,
                stake_yes=new_stake,
                stake_no=old_position.stake_no,
            ),
            -sign * transaction.amount,
        )
    else:
        new_stake = old_position.stake_no + sign * transaction.amount / price
        assert new_stake >= 0
        return (
            Position(
                user_id=old_position.user_id,
                question_id=old_position.question_id,
                stake_yes=old_position.stake_yes,
                stake_no=new_stake,
            ),
            -sign * transaction.amount,
        )
