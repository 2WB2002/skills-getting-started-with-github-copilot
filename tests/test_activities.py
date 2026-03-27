"""Tests for activity management endpoints using the AAA (Arrange-Act-Assert) pattern."""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """Should return a list of all available activities."""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Club",
            "Science Club",
            "Debate Team",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_activity_details(self, client: TestClient):
        """Should return activity details including description, schedule, and participants."""
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert expected_keys.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestRootRedirect:
    """Test suite for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client: TestClient):
        """Should redirect root path to static index.html."""
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follows_to_index(self, client: TestClient):
        """Should successfully follow redirect to index.html."""
        # Arrange
        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_adds_student_to_activity(self, client: TestClient):
        """Should successfully add a student to an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_fails_for_nonexistent_activity(self, client: TestClient):
        """Should return 404 when trying to sign up for a nonexistent activity."""
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_fails_for_duplicate_student(self, client: TestClient):
        """Should return 400 when student is already signed up for activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_with_special_characters_in_email(self, client: TestClient):
        """Should handle emails with special characters."""
        # Arrange
        activity_name = "Tennis Club"
        email = "student.name+special@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_multiple_students_to_same_activity(self, client: TestClient):
        """Should successfully add multiple different students to the same activity."""
        # Arrange
        activity_name = "Art Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
