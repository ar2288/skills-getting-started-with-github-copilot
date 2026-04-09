import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store initial state
    initial_activities = {
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
        },
        "Basketball Team": {
            "description": "Competitive basketball team and practice",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and matches",
            "schedule": "Tuesdays and Thursdays, 3:45 PM - 5:15 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu", "ryan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Drawing, painting, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performance and acting workshops",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "aiden@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore physics, chemistry, and biology through experiments",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "connor@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(initial_activities)
    yield


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_success():
    response = client.post("/activities/Chess Club/signup", params={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Chess Club" in data["message"]
    # Check that participant was added
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent Activity/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "test@example.com"})
    # Try again
    response = client.post("/activities/Chess Club/signup", params={"email": "test@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_unregister_success():
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "test@example.com"})
    # Then unregister
    response = client.delete("/activities/Chess Club/unregister", params={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Chess Club" in data["message"]
    # Check that participant was removed
    assert "test@example.com" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/NonExistent Activity/unregister", params={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess Club/unregister", params={"email": "notsigned@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]