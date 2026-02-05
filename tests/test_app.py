"""
Test suite for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from sys import path as sys_path
from pathlib import Path

# Add src directory to path for imports
sys_path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that GET /activities returns all expected activities"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Basketball Club",
            "Tennis Team",
            "Art Studio",
            "Music Band",
            "Debate Team",
            "Science Club"
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200_on_success(self):
        """Test that signup returns status 200 on success"""
        response = client.post(
            "/activities/Basketball%20Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self):
        """Test that signup returns success message"""
        response = client.post(
            "/activities/Basketball%20Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student2@mergington.edu" in data["message"]
        assert "Basketball Club" in data["message"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup adds participant to activity"""
        email = "student3@mergington.edu"
        client.post(
            "/activities/Tennis%20Team/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Team"]["participants"]

    def test_signup_fails_for_nonexistent_activity(self):
        """Test that signup fails for nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_fails_if_already_registered(self):
        """Test that signup fails if student already registered"""
        email = "student4@mergington.edu"
        
        # First signup succeeds
        response1 = client.post(
            "/activities/Art%20Studio/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup for same activity fails
        response2 = client.post(
            "/activities/Art%20Studio/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_works_for_same_student_different_activities(self):
        """Test that same student can signup for different activities"""
        email = "student5@mergington.edu"
        
        response1 = client.post(
            "/activities/Music%20Band/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Debate%20Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Music Band"]["participants"]
        assert email in activities["Debate Team"]["participants"]


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_returns_200_on_success(self):
        """Test that unregister returns status 200 on success"""
        email = "student6@mergington.edu"
        
        # First signup
        client.post(
            "/activities/Science%20Club/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Science%20Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self):
        """Test that unregister returns success message"""
        email = "student7@mergington.edu"
        
        client.post(
            "/activities/Basketball%20Club/signup",
            params={"email": email}
        )
        
        response = client.delete(
            "/activities/Basketball%20Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Basketball Club" in data["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        email = "student8@mergington.edu"
        
        # Signup first
        client.post(
            "/activities/Tennis%20Team/signup",
            params={"email": email}
        )
        
        # Verify participant is there
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Team"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Tennis%20Team/unregister",
            params={"email": email}
        )
        
        # Verify participant is removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Tennis Team"]["participants"]

    def test_unregister_fails_for_nonexistent_activity(self):
        """Test that unregister fails for nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_fails_if_not_registered(self):
        """Test that unregister fails if student not registered"""
        response = client.delete(
            "/activities/Art%20Studio/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]


class TestRootEndpoint:
    """Test the GET / endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
