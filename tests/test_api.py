import requests
import pytest
from polymarket_predictions_tally.api import get_questions_by_id_list


# Create a fake response class that mimics the behavior of requests.Response
class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("Bad status")

    def json(self):
        return self._json


def test_get_questions_by_id_list(monkeypatch):
    # Prepare a fake payload that simulates the API response.
    fake_payload = [
        {
            "id": 1,
            "question": "Test Q1",
            "tag": "Politics",
            "outcome": None,
            "outcomePrices": "[0.8, 0.2]",
            "outcomes": '["Yes", "No"]',
            "endDate": "2025-02-14 00:00:00",
            "description": "desc",
            "unaccessed_data": "whatever",
        },
        {
            "id": 2,
            "question": "Test Q2",
            "tag": "Politics",
            "outcome": "Yes",
            "outcomePrices": "[0.8, 0.2]",
            "outcomes": '["Yes", "No"]',
            "endDate": "2025-02-15 00:00:00",
            "description": "desc",
            "unaccessed_data": "whatever",
        },
        {
            "id": 2,
            "question": "Test Q2",
            "tag": "Politics",
            "outcome": "Yes",
            "outcomePrices": "[0.8, 0.2]",
            "outcomes": '["Yes", "No"]',
            "description": "desc",
            "unaccessed_data": "whatever",
        },
    ]

    # Define a fake requests.get that returns our fake payload.
    def fake_get(url, params):
        # Optionally, you can assert that url and params are what you expect.
        assert url == "https://gamma-api.polymarket.com/markets"
        # For example, check that params is a list of tuples with "id" as key.
        # (We don't need to be too strict in the test unless you want to.)
        return FakeResponse(fake_payload, 200)

    # Use monkeypatch to replace requests.get with our fake_get.
    monkeypatch.setattr(requests, "get", fake_get)

    # Call the function with a test id_list.
    id_list = [1, 2]
    results = get_questions_by_id_list(id_list)

    # Now assert that the results are as expected.
    assert isinstance(results, list)
    assert len(results) == 3
    # Check that the first market has the expected question text.
    assert not (results[0] is None)
    assert results[0].question == "Test Q1"
    # And the second has the expected id.
    assert not results[1] is None
    assert results[1].id == 2
    assert results[2] is None
