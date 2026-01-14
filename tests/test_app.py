"""
Tests for the FastAPI activities application
"""
import pytest
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self):
        """Test that signup adds participant to the activity"""
        email = "testsignup@mergington.edu"
        # Get initial participants count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1
        assert email in response.json()["Chess Club"]["participants"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered(self):
        """Test signup fails if student is already registered"""
        email = "duplicate@mergington.edu"
        activity = "Programming Class"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_with_special_characters_in_email(self):
        """Test signup with email containing special characters"""
        response = client.post(
            "/activities/Science%20Club/signup",
            params={"email": "test+tag@mergington.edu"}
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        email = "testunregister@mergington.edu"
        activity = "Basketball Team"
        
        # First sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from the activity"""
        email = "removetest@mergington.edu"
        activity = "Soccer Club"
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get count after signup
        response = client.get("/activities")
        count_after_signup = len(response.json()[activity]["participants"])
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        count_after_unregister = len(response.json()[activity]["participants"])
        assert count_after_unregister == count_after_signup - 1
        assert email not in response.json()[activity]["participants"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self):
        """Test unregister fails if student is not registered"""
        response = client.post(
            "/activities/Art%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_with_special_characters_in_email(self):
        """Test unregister with email containing special characters"""
        email = "special+test@mergington.edu"
        activity = "Drama Club"
        
        # Sign up first
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200


class TestRootRedirect:
    """Tests for root endpoint redirect"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
