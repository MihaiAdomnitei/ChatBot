"""
Test Suite - API Integration Tests

Tests for the Medical AI Chatbot API endpoints.
Uses pytest with httpx for async testing.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def mock_engine():
    """Create a mock PatientChatEngine."""
    engine = Mock()
    engine.generate.return_value = "I have a sharp pain in my lower right tooth."
    return engine


@pytest.fixture
def app_client(mock_engine):
    """Create a test client with mocked engine."""
    # Import here to avoid loading model
    with patch.dict(os.environ, {"LOAD_MODEL_ON_STARTUP": "false"}):
        from backend.app import create_app
        from backend.api.dependencies import set_engine, set_chat_manager
        from backend.ai import ChatManager

        app = create_app()

        # Set up mocks
        set_engine(mock_engine)
        chat_manager = ChatManager()
        set_chat_manager(chat_manager)

        with TestClient(app) as client:
            yield client


# ============================================
# Health Check Tests
# ============================================

class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, app_client):
        """Test basic health check."""
        response = app_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data

    def test_readiness_check(self, app_client):
        """Test readiness probe."""
        response = app_client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ready", "not_ready"]

    def test_liveness_check(self, app_client):
        """Test liveness probe."""
        response = app_client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


# ============================================
# Chat Session Tests
# ============================================

class TestChatEndpoints:
    """Tests for chat session endpoints."""

    def test_create_chat_random_pathology(self, app_client):
        """Test creating a chat with random pathology."""
        response = app_client.post("/chats", json={})
        assert response.status_code == 201
        data = response.json()
        assert "chat_id" in data
        assert "pathology" in data
        assert "created_at" in data

    def test_create_chat_specific_pathology(self, app_client):
        """Test creating a chat with specific pathology."""
        response = app_client.post("/chats", json={"pathology": "dental_caries"})
        assert response.status_code == 201
        data = response.json()
        assert data["pathology"] == "dental_caries"

    def test_create_chat_invalid_pathology(self, app_client):
        """Test creating a chat with invalid pathology."""
        response = app_client.post("/chats", json={"pathology": "invalid_disease"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_PATHOLOGY"

    def test_list_chats(self, app_client):
        """Test listing chat sessions."""
        # Create a chat first
        app_client.post("/chats", json={})

        response = app_client.get("/chats")
        assert response.status_code == 200
        data = response.json()
        assert "chats" in data
        assert "total" in data
        assert len(data["chats"]) >= 1

    def test_get_chat_details(self, app_client):
        """Test getting chat details."""
        # Create a chat
        create_response = app_client.post("/chats", json={})
        chat_id = create_response.json()["chat_id"]

        response = app_client.get(f"/chats/{chat_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["chat_id"] == chat_id
        assert "messages" in data

    def test_get_chat_not_found(self, app_client):
        """Test getting non-existent chat."""
        response = app_client.get("/chats/non-existent-id")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "CHAT_NOT_FOUND"

    def test_delete_chat(self, app_client):
        """Test deleting a chat."""
        # Create a chat
        create_response = app_client.post("/chats", json={})
        chat_id = create_response.json()["chat_id"]

        # Delete it
        response = app_client.delete(f"/chats/{chat_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = app_client.get(f"/chats/{chat_id}")
        assert response.status_code == 404

    def test_reset_chat(self, app_client):
        """Test resetting a chat."""
        # Create a chat and send a message
        create_response = app_client.post("/chats", json={})
        chat_id = create_response.json()["chat_id"]

        # Reset it
        response = app_client.post(f"/chats/{chat_id}/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["chat_id"] == chat_id


# ============================================
# Message Tests
# ============================================

class TestMessageEndpoints:
    """Tests for message sending endpoints."""

    def test_send_message(self, app_client, mock_engine):
        """Test sending a message."""
        # Create a chat
        create_response = app_client.post("/chats", json={})
        chat_id = create_response.json()["chat_id"]

        # Send a message
        response = app_client.post(
            f"/chats/{chat_id}/message",
            json={"message": "Where does it hurt?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert data["chat_id"] == chat_id
        assert data["message_count"] > 1

    def test_send_message_with_params(self, app_client):
        """Test sending a message with custom parameters."""
        create_response = app_client.post("/chats", json={})
        chat_id = create_response.json()["chat_id"]

        response = app_client.post(
            f"/chats/{chat_id}/message",
            json={
                "message": "Describe the pain",
                "max_new_tokens": 50,
                "temperature": 0.3
            }
        )
        assert response.status_code == 200

    def test_send_message_to_nonexistent_chat(self, app_client):
        """Test sending message to non-existent chat."""
        response = app_client.post(
            "/chats/fake-chat-id/message",
            json={"message": "Hello"}
        )
        assert response.status_code == 404


# ============================================
# Pathology Tests
# ============================================

class TestPathologyEndpoints:
    """Tests for pathology listing endpoint."""

    def test_list_pathologies(self, app_client):
        """Test listing available pathologies."""
        response = app_client.get("/chats/pathologies/list")
        assert response.status_code == 200
        data = response.json()
        assert "pathologies" in data
        assert "total" in data
        assert data["total"] > 0

        # Check structure
        pathology = data["pathologies"][0]
        assert "key" in pathology
        assert "label" in pathology
        assert "chief_complaint" in pathology


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

