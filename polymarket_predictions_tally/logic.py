from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json
from datetime import datetime

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

    @classmethod
    def from_database_entry(
        cls,
        entry: tuple[int, str, str, str, str, Optional[bool], str, str],
    ) -> "Question":
        (id, question, outcome_probs, outcomes, tag, outcome, end_date, description) = (
            entry
        )

        outcome_probs = json.loads(outcome_probs)  # Convert string to list[float]
        outcomes = json.loads(outcomes)  # Convert string to list[str]
        end_date = datetime.fromisoformat(end_date)  # Convert string to datetime

        return cls(
            id, question, outcome_probs, outcomes, tag, outcome, end_date, description
        )

    def __str__(self) -> str:
        date_str = self.end_date.strftime("%b %d, %Y")  # Short readable date
        outcomes_str = " ".join(
            f"{o}: {p:.2f}" for o, p in zip(self.outcomes, self.outcome_probs)
        )
        short_desc = self.description.split("\n")[0][:100]  # First line, max 100 chars
        return f"""Question {self.id}: {self.question}
\t[{self.tag}]
\tEnds:           {date_str}
\tProbabilities:  {outcomes_str}
\tDescription:    {short_desc}...
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


@dataclass(frozen=True)
class User:
    id: int
    username: str
    budget: int


@dataclass
class Response:
    user_id: int
    question_id: int
    answer: str
    timestamp: datetime
    correct: Optional[bool]
    explanation: Optional[str]

    @classmethod
    def from_database_entry(
        cls, entry: tuple[int, int, int, str, str, Optional[bool], Optional[str]]
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
            user_id,
            question_id,
            answer,
            timestamp,
            correct,
            explanation,
        )


class InvalidResponse(Exception):
    pass


@dataclass
class Transaction:
    user_id: int
    question_id: int
    transaction_type: str  # eg buy or sell
    answer: bool  # yes or no
    amount: float


@dataclass
class Position:
    user_id: int
    question_id: int
    stake_yes: float
    stake_no: float
