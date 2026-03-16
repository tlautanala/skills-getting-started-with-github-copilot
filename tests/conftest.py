import pytest
from fastapi.testclient import TestClient
from src.app import app
import copy


@pytest.fixture
def client():
    """Returns a TestClient instance for making HTTP requests to the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def activities_data():
    """Returns a fresh copy of test activities data for isolation."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }


@pytest.fixture(autouse=True)
def mock_activities(monkeypatch, activities_data):
    """Automatically patches app.activities with fresh test data before each test."""
    from src import app as app_module
    monkeypatch.setattr(app_module, 'activities', copy.deepcopy(activities_data))