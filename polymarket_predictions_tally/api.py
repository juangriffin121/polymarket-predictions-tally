from typing import List
from datetime import datetime, timedelta, timezone
import requests
import json
from polymarket_predictions_tally.logic import Event, Question
from polymarket_predictions_tally.constants import MAX_TIME_DELTA_DAYS, MAX_QUESTIONS


tag_names = {1: "Sports", 2: "Politics", 3: "Other"}
tag_ids = {"Sports": 1, "Politics": 2, "Other": 3}


def get_questions(tag: str, limit: int = MAX_QUESTIONS) -> List[Question]:
    endpoint = "https://gamma-api.polymarket.com/markets"
    data = fetch_data(tag, endpoint, limit)
    return get_questions_from_data(tag, data)


def get_events(tag: str, limit: int = 3) -> List[Event]:
    endpoint = "https://gamma-api.polymarket.com/events"
    data = fetch_data(tag, endpoint, limit)
    return get_events_from_data(tag, data)


def get_question_raw(id: int) -> dict:
    endpoint = "https://gamma-api.polymarket.com/markets"
    params = {"id": id}
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()


def get_question(id: int, tag: str) -> Question | None:
    question = get_question_raw(id)
    return get_question_from_entry(question, tag)


def get_event_raw(id: int) -> dict:
    endpoint = "https://gamma-api.polymarket.com/events"
    params = {"id": id}
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()


def get_events_from_data(tag: str, data: List[dict]) -> List[Event]:
    events = []
    for entry in data:
        events.append(get_event_from_entry(entry, tag))
    return events


def get_event(id: int, tag: str) -> Event:
    question = get_event_raw(id)
    return get_event_from_entry(question, tag)


def get_questions_from_data(tag: str, data: List[dict]) -> List[Question]:
    questions = []
    for entry in data:
        if not entry.get("active"):
            continue
        question = get_question_from_entry(entry, tag)
        if not question:
            continue
        questions.append(question)
    return questions


def get_question_from_entry(entry: dict, tag: str) -> Question | None:
    try:
        end_date = datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00"))
    except:
        try:
            end_date = datetime.fromisoformat(entry["endDateIso"])
        except:
            return None

    return Question(
        id=int(entry["id"]),
        question=entry["question"],
        outcome_probs=[float(p) for p in json.loads(entry["outcomePrices"])],
        outcomes=json.loads(entry["outcomes"]),
        tag=tag,
        outcome=get_resolved_outcome(entry),
        end_date=end_date,
        description=entry["description"],
    )


def get_event_from_entry(entry: dict, tag: str) -> Event:
    markets = entry["markets"]
    questions = get_questions_from_data(tag, markets)
    return Event(
        id=int(entry["id"]),
        title=entry["title"],
        questions=questions,
        end_date=datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00")),
    )


def fetch_data(
    tag: str,
    endpoint: str,
    limit: int,
) -> List[dict]:
    try:
        tag_id = tag_ids[tag]
    except Exception as e:
        raise e
    params = {
        "active": "true",
        "closed": "false",
        "limit": limit,
        "tag_id": tag_id,
        "ascending": "false",
        "order": "volume",
        "end_date_min": (datetime.now(tz=timezone.utc) + timedelta(days=1)).isoformat(),
        "end_date_max": (
            datetime.now(tz=timezone.utc) + timedelta(days=MAX_TIME_DELTA_DAYS)
        ).isoformat(),
    }

    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()


def get_questions_by_id_list(id_list: list[int]) -> list[Question | None]:
    endpoint = "https://gamma-api.polymarket.com/markets"
    # Create a list of tuples for each id
    params = [("id", str(id)) for id in id_list]
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    # Assuming the API returns a dict with the key "markets"
    return [
        get_question_from_entry(entry, tag="Politics") for entry in response.json()
    ]  # .json().get("markets", [])


def get_resolved_outcome(entry: dict) -> bool | None:
    """
    Returns:
        - True: Market resolved to "Yes"
        - False: Market resolved to "No"
        - None: Market not resolved or data format error
    """

    resolved_status = entry.get("umaResolutionStatus")

    if resolved_status is not None and resolved_status != "resolved":
        print(f"{entry.get('question')} had resolved status not resolved")
        return None
    # Check if market is resolved
    try:
        end_date = datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00"))
    except:
        try:
            end_date = datetime.fromisoformat(entry["endDateIso"])
        except:
            end_date = None

    if end_date is not None and end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    if end_date is not None and end_date > datetime.now(timezone.utc):
        # print(f"[{end_date}] {entry.get('question')} hasnt reached its end date")
        return None

    try:
        # Parse outcome prices and labels
        outcome_prices = json.loads(entry["outcomePrices"])
        outcomes = json.loads(entry["outcomes"])

        # Find the winning outcome index (price == "1")
        winning_idx = next(
            (i for i, price in enumerate(outcome_prices) if price == "1"), None
        )

        if winning_idx is None or winning_idx >= len(outcomes):
            print("Reached an unexpected point, useful info for debuging")
            print(f"[{end_date}] {entry.get('question')} escaped from winning_idx")
            print(outcome_prices)
            print(outcomes)
            print()

            return None  # No valid winning outcome

        return outcomes[winning_idx] == "Yes"

    except (KeyError, json.JSONDecodeError):
        print(KeyError, json.JSONDecodeError)
        return None  # Handle missing fields or invalid JSON
