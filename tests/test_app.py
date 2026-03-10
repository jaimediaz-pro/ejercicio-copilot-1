"""Pytest tests for the Mergington High School API FastAPI app."""

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Snapshot and restore the activities dict before and after each test."""
    snapshot = {
        key: {
            **value,
            "participants": value["participants"].copy(),
        }
        for key, value in activities.items()
    }

    yield

    activities.clear()
    for key, value in snapshot.items():
        activities[key] = {
            **value,
            "participants": value["participants"].copy(),
        }


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    expected_activities = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Swim Club",
        "Art Studio",
        "Drama Club",
        "Science Olympiad",
        "Debate Team",
    }
    assert set(data.keys()) == expected_activities


def test_signup_adds_participant(client):
    email = "newstudent@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    activities_data = client.get("/activities").json()
    assert email in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    email = "michael@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response.status_code == 400


def test_remove_participant(client):
    email = "removeme@mergington.edu"

    client.post(
        "/activities/Programming Class/signup",
        params={"email": email},
    )

    response = client.delete(
        "/activities/Programming Class/participants",
        params={"email": email},
    )
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    activities_data = client.get("/activities").json()
    assert email not in activities_data["Programming Class"]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    email = "notthere@mergington.edu"

    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]
