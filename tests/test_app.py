import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    response = client.post(
        "/activities/Chess%20Club/signup?email=test.student@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test.student@mergington.edu for Chess Club"
    assert "test.student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    email = "emma@mergington.edu"
    response = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity():
    response = client.post(
        "/activities/Unknown%20Group/signup?email=test.student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_successfully():
    email = "john@mergington.edu"
    response = client.delete(
        f"/activities/Gym%20Class/participants?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed john@mergington.edu from Gym Class"
    assert email not in activities["Gym Class"]["participants"]


def test_remove_participant_returns_404_for_missing_participant():
    response = client.delete(
        "/activities/Gym%20Class/participants?email=missing.student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
