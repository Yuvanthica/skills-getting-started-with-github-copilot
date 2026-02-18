import pytest


def test_root_redirect(client):
    """Test that root path redirects to index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    """Test fetching all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Check activity structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity(client, reset_activities):
    """Test signing up for an activity."""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newemail@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "newemail@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    chess_club = activities_response.json()["Chess Club"]
    assert "newemail@mergington.edu" in chess_club["participants"]


def test_signup_duplicate_fails(client, reset_activities):
    """Test that signing up twice for the same activity fails."""
    email = "test@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_invalid_activity(client):
    """Test signing up for non-existent activity."""
    response = client.post(
        "/activities/Invalid%20Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_signup_activity_full(client, reset_activities):
    """Test that signup fails when activity is at capacity."""
    # Tennis Club has max 12 participants, currently has 1
    # Add 11 more to reach capacity
    for i in range(11):
        client.post(
            f"/activities/Tennis%20Club/signup?email=student{i}@mergington.edu"
        )
    
    # Next signup should fail (capacity reached)
    response = client.post(
        "/activities/Tennis%20Club/signup?email=overflow@mergington.edu"
    )
    assert response.status_code == 400
    assert "full" in response.json()["detail"]


def test_unregister_from_activity(client, reset_activities):
    """Test unregistering from an activity."""
    email = "testuser@mergington.edu"
    
    # First, sign up
    client.post(
        f"/activities/Drama%20Club/signup?email={email}"
    )
    
    # Then unregister
    response = client.post(
        f"/activities/Drama%20Club/unregister?email={email}"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    drama_club = activities_response.json()["Drama Club"]
    assert email not in drama_club["participants"]


def test_unregister_invalid_activity(client):
    """Test unregistering from non-existent activity."""
    response = client.post(
        "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404


def test_unregister_not_registered(client, reset_activities):
    """Test unregistering when not registered fails."""
    response = client.post(
        "/activities/Science%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_activity_capacity_values(client):
    """Test that activity capacity values are correct."""
    response = client.get("/activities")
    data = response.json()
    
    # Check specific activities
    assert data["Chess Club"]["max_participants"] == 12
    assert data["Programming Class"]["max_participants"] == 20
    assert data["Gym Class"]["max_participants"] == 30
    assert data["Basketball Team"]["max_participants"] == 15


def test_initial_participants(client):
    """Test that initial participants are loaded correctly."""
    response = client.get("/activities")
    data = response.json()
    
    # Chess Club should have initial participants
    assert len(data["Chess Club"]["participants"]) == 2
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    
    # Basketball Team should have 1 participant
    assert len(data["Basketball Team"]["participants"]) == 1
    assert "alex@mergington.edu" in data["Basketball Team"]["participants"]
