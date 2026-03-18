"""Tests for Pydantic schema validation."""

import pytest
from pydantic import ValidationError

from src.models.schemas import LogEvent


def test_valid_log_event():
    """Test creating a LogEvent with valid data."""
    event_data = {
        "timestamp": "2026-03-18T22:00:00Z",
        "source_ip": "192.168.1.5",
        "destination_ip": "192.168.1.10",
        "destination_port": 80,
        "protocol": "TCP",
        "event_type": "connection",
        "raw_log": "raw log string",
    }

    event = LogEvent(**event_data)
    assert event.source_ip == "192.168.1.5"
    assert event.destination_port == 80


def test_invalid_log_event():
    """Test creating a LogEvent with invalid data."""
    event_data = {
        "timestamp": "2026-03-18T22:00:00Z",
        "source_ip": "192.168.1.5",
        "destination_ip": "192.168.1.10",
        "destination_port": "not-a-port",
        "protocol": "TCP",
        "event_type": "connection",
        "raw_log": "raw log string",
    }

    with pytest.raises(ValidationError):
        LogEvent(**event_data)
