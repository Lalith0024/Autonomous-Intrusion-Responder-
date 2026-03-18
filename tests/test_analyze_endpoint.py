"""Tests for the analyze API endpoint."""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()


def test_analyze_invalid_input():
    """Test the analyze endpoint rejects invalid payloads."""
    # Missing required fields like destination_port, protocol, etc.
    invalid_payload = {
        "timestamp": "2026-03-18T22:00:00Z",
        "source_ip": "45.33.32.156",
    }
    response = client.post("/analyze", json=invalid_payload)
    assert response.status_code == 422
