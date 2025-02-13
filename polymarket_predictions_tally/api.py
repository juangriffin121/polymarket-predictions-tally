from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import requests
import json


@dataclass
class Question:
    id: int
    question: str
    outcome_probs: List[float]
    outcomes: List[str]
    tag: str
    outcome: Optional[bool]
    end_date: datetime
    description: str

    def __str__(self) -> str:
        date_str = self.end_date.strftime("%b %d, %Y")  # Short readable date
        outcomes_str = " ".join(
            f"{o}: {p:.2f}" for o, p in zip(self.outcomes, self.outcome_probs)
        )
        short_desc = self.description.split("\n")[0][:100]  # First line, max 100 chars
        return f"Question {self.id}: {self.question}\n\t[{self.tag}]\n\tEnds:\t\t{date_str}\n\tProbabilities:\t{outcomes_str} \n\tDescription:\t{short_desc}...\n"


@dataclass
class Event:
    id: int
    title: str
    questions: List[Question]
    end_date: datetime

    def __str__(self) -> str:
        date_str = self.end_date.strftime("%b %d, %Y")
        return (
            f"Event: {self.title} (Ends: {date_str}) | {len(self.questions)} questions"
        )


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


def get_question(id: int) -> Question:
    endpoint = "https://gamma-api.polymarket.com/markets"
    params = {"id": id}
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()


def get_events_from_data(tag: str, data: List[dict]) -> List[Event]:
    events = []
    for entry in data:
        markets = entry["markets"]
        questions = get_questions_from_data(tag, markets)
        events.append(
            Event(
                id=int(entry["id"]),
                title=entry["title"],
                questions=questions,
                end_date=datetime.fromisoformat(
                    entry["endDate"].replace("Z", "+00:00")
                ),
            )
        )
    return events


def get_questions_from_data(tag: str, data: List[dict]) -> List[Question]:
    # The response is expected to have a "data" key with a loist of markets.
    questions = []
    for entry in data:
        if not entry.get("active"):
            continue

        questions.append(
            Question(
                id=int(entry["id"]),
                question=entry["question"],
                outcome_probs=[float(p) for p in json.loads(entry["outcomePrices"])],
                outcomes=json.loads(entry["outcomes"]),
                tag=tag,
                outcome=None,
                end_date=datetime.fromisoformat(
                    entry["endDate"].replace("Z", "+00:00")
                ),
                description=entry["description"],
            )
        )
    return questions


def get_question_from_entry(entry: dict, tag: str):
    Question(
        id=int(entry["id"]),
        question=entry["question"],
        outcome_probs=[float(p) for p in json.loads(entry["outcomePrices"])],
        outcomes=json.loads(entry["outcomes"]),
        tag=tag,
        outcome=None,
        end_date=datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00")),
        description=entry["description"],
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
    # Gamma Markets API endpoint for fetching markets.
    params = {
        # "active": "true",
        "closed": "false",
        "limit": limit,
        "tag_id": tag_id,
        "ascending": "false",
        "order": "volume",
    }

    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()
