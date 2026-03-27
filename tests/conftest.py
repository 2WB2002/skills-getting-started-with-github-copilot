"""Shared test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for testing the FastAPI application."""
    return TestClient(app)
