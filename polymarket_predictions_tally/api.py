from typing import List
from datetime import datetime
import requests
import json
from polymarket_predictions_tally.logic import Event, Question


tag_names = {1: "Sports", 2: "Politics", 3: "Other"}
tag_ids = {"Sports": 1, "Politics": 2, "Other": 3}


def get_questions(tag: str, limit: int = 100) -> List[Question]:
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
        outcome=None,
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
    limit: int = 100,
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
