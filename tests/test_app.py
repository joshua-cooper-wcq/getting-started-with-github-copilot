from fastapi.testclient import TestClient

from src.app import activities


def test_root_redirects_to_static_index(client: TestClient):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_initial_state(client: TestClient):
    # Arrange
    expected_participants = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_activities = response.json()
    assert set(response_activities) == set(activities)
    assert response_activities["Chess Club"]["participants"] == expected_participants
    assert response_activities["Chess Club"]["max_participants"] == 12


def test_signup_adds_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_rejects_duplicate_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}
    assert activities[activity_name]["participants"] == original_participants


def test_signup_rejects_when_activity_is_full(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    current_participants = activities[activity_name]["participants"]
    max_participants = activities[activity_name]["max_participants"]

    # Fill activity to capacity
    for i in range(max_participants - len(current_participants)):
        current_participants.append(f"filler{i}@mergington.edu")

    email = "late.student@mergington.edu"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert activities[activity_name]["participants"] == original_participants

def test_signup_rejects_unknown_activity(client: TestClient):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    assert activities[activity_name]["participants"] == original_participants


def test_unregister_removes_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    remaining_participant = "daniel@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]
    assert remaining_participant in activities[activity_name]["participants"]


def test_unregister_rejects_missing_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}
    assert activities[activity_name]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(client: TestClient):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Activity/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_requires_email(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister")

    # Assert
    assert response.status_code == 422
    assert activities[activity_name]["participants"] == original_participants