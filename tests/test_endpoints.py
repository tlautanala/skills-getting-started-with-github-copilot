"""Tests for FastAPI endpoints."""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint (GET /)."""

    def test_root_redirect(self, client):
        """Test that GET / redirects to /static/index.html."""
        # TestClient follows redirects by default, so we get 200 from the final destination
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint (GET /activities)."""

    def test_get_activities_success(self, client, activities_data):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 3  # We have 3 test activities

        # Verify structure of first activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_structure(self, client, activities_data):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        data = response.json()

        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert all(isinstance(email, str) for email in activity_data["participants"])


class TestSignupEndpoint:
    """Tests for the signup endpoint (POST /activities/{activity_name}/signup)."""

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/NonExistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client):
        """Test that signing up twice returns 400 error."""
        # First signup should succeed
        response1 = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response1.status_code == 200

        # Second signup should fail
        response2 = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_preserves_existing_participants(self, client):
        """Test that signup doesn't affect other participants."""
        # Get initial participants from the activities endpoint
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = initial_data["Chess Club"]["participants"].copy()

        # Add new participant
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "new@mergington.edu"}
        )

        # Check that original participants are still there
        response = client.get("/activities")
        final_data = response.json()
        assert set(initial_participants).issubset(set(final_data["Chess Club"]["participants"]))
        assert "new@mergington.edu" in final_data["Chess Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint (DELETE /activities/{activity_name}/unregister)."""

    def test_unregister_success(self, client):
        """Test successful removal of a participant."""
        # First add a participant to remove
        client.post(
            "/activities/Gym%20Class/signup",
            params={"email": "toremove@mergington.edu"}
        )

        # Now remove them
        response = client.delete(
            "/activities/Gym%20Class/unregister",
            params={"email": "toremove@mergington.edu"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "toremove@mergington.edu" in data["message"]
        assert "Gym Class" in data["message"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_found(self, client):
        """Test unregistering a non-participant returns 400."""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "notsignedup@mergington.edu"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_unregister_preserves_other_participants(self, client):
        """Test that unregistering one participant doesn't affect others."""
        # Add two participants
        client.post("/activities/Programming%20Class/signup", params={"email": "keep@mergington.edu"})
        client.post("/activities/Programming%20Class/signup", params={"email": "remove@mergington.edu"})

        # Remove one
        client.delete("/activities/Programming%20Class/unregister", params={"email": "remove@mergington.edu"})

        # Check that the other is still there
        response = client.get("/activities")
        data = response.json()
        assert "keep@mergington.edu" in data["Programming Class"]["participants"]
        assert "remove@mergington.edu" not in data["Programming Class"]["participants"]