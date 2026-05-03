import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

@pytest.fixture
def mock_firebase():
    with patch('main.db') as mock_db, patch('main.verify_token') as mock_verify:
        yield mock_db, mock_verify

# --- SUCCESS CASES ---

def test_get_states():
    response = client.get("/states")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_authorized_get_user(mock_firebase):
    mock_db, mock_verify = mock_firebase
    mock_verify.return_value = {"uid": "test_uid"}
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"username": "testuser", "xp": 100}
    mock_db.collection().document().get.return_value = mock_doc
    
    for endpoint in ["/user/me", "/login"]:
        response = client.get(endpoint, headers={"Authorization": "Bearer fake_token"})
        assert response.status_code == 200
        assert "username" in response.json()

# --- FAILURE & EDGE CASES ---

def test_unauthorized_access():
    response = client.get("/user/me")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_invalid_token(mock_firebase):
    _, mock_verify = mock_firebase
    mock_verify.return_value = None
    response = client.get("/user/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401

def test_missing_fields_play_turn(mock_firebase):
    _, mock_verify = mock_firebase
    mock_verify.return_value = {"uid": "test_uid"}
    # Missing 'state' and 'session_id'
    response = client.post(
        "/play-turn",
        json={"message": "Hello"},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 422 # Unprocessable Entity (FastAPI validation)

def test_empty_input_signup(mock_firebase):
    _, mock_verify = mock_firebase
    mock_verify.return_value = {"uid": "test_uid"}
    response = client.post(
        "/signup",
        json={}, # Empty JSON
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200 # Optional fields make this valid, but let's check response
    assert response.json()["status"] == "success"

def test_invalid_type_add_xp(mock_firebase):
    _, mock_verify = mock_firebase
    mock_verify.return_value = {"uid": "test_uid"}
    response = client.post(
        "/add-xp",
        json={"points": "fifty"}, # String instead of int
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 422

def test_negative_xp_validation(mock_firebase):
    mock_db, mock_verify = mock_firebase
    mock_verify.return_value = {"uid": "test_uid"}
    
    response = client.post(
        "/add-xp",
        json={"points": -50},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Points cannot be negative"

def test_user_not_found_xp(mock_firebase):
    mock_db, mock_verify = mock_firebase
    mock_verify.return_value = {"uid": "ghost_uid"}
    
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = None # User doesn't exist in DB
    mock_db.collection().document().get.return_value = mock_doc
    
    response = client.post(
        "/add-xp",
        json={"points": 10},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 404

# --- SCHEMA VALIDATION ---

def test_response_schema_timeline():
    response = client.get("/timeline/Karnataka")
    assert response.status_code == 200
    data = response.json()
    required_keys = ["polling_day", "registration_deadline", "result_day"]
    for key in required_keys:
        assert key in data
