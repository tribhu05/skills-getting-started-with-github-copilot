import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activity participants before each test to ensure test isolation."""
    # Arrange: snapshot initial state
    original_participants = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    # Cleanup / Reset after test
    for name, participants in original_participants.items():
        activities[name]["participants"] = list(participants)


def test_get_activities():
    # Arrange: none required

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Gym Class" in data
    assert "description" in data["Chess Club"]


def test_signup_success():
    # Arrange
    activity_name = "Basketball Team"
    email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_fails():
    # Arrange
    activity_name = "Chess Club"
    existing_student = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_student})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    student = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": student})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {student} from {activity_name}"
    assert student not in activities[activity_name]["participants"]


def test_unregister_not_signed_up_fails():
    # Arrange
    activity_name = "Basketball Team"
    student = "not_enrolled@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": student})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up"


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    student = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": student})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
