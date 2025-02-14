from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import List, Optional, Tuple

from polymarket_predictions_tally.utils import parse_datetime


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
        return f"""
            Question {self.id}: {self.question}
                [{self.tag}]
                Ends:           {date_str}
                Probabilities:  {outcomes_str}
                Description:    {short_desc}...
            """


@dataclass
class Event:
    id: int
    title: str
    questions: List[Question]
    end_date: datetime

    def __str__(self) -> str:
        date_str = self.end_date.strftime("%b %d, %Y")
        return f"Event {self.id}: {self.title} (Ends: {date_str}) | {len(self.questions)} questions"


@dataclass
class User:
    id: int
    username: str
    budget: int


@dataclass
class Response:
    id: int
    user_id: int
    question_id: int
    answer: str
    timestamp: datetime
    correct: Optional[bool]
    explanation: Optional[str]

    @classmethod
    def from_database_entry(
        cls, entry: Tuple[int, int, int, str, str, Optional[bool], Optional[str]]
    ) -> "Response":
        (
            response_id,
            user_id,
            question_id,
            answer,
            timestamp,
            correct,
            explanation,
        ) = entry

        timestamp = parse_datetime(timestamp)

        return cls(
            response_id,
            user_id,
            question_id,
            answer,
            timestamp,
            correct,
            explanation,
        )


class InvalidResponse(Exception):
    pass
