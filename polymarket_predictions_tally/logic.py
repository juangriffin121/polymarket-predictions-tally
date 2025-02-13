from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Question:
    id: int
    question: str
    outcome_probs: List[float]
    outcomes: List[str]
    tag: str
    resolved: bool
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


class User:
    id: int
    username: str
    budget: int


@dataclass
class response:
    id: int
    user_id: int
    question_id: int
    answer: str
    timestamp: datetime
    correct: Optional[bool]
