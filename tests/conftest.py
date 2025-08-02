import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import get_db


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    return Mock(spec=Session)


@pytest.fixture
def override_get_db(mock_db_session):
    """Override the database dependency for testing"""
    def _override_get_db():
        return mock_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield mock_db_session
    app.dependency_overrides.clear()


@pytest.fixture
def sample_post_data():
    """Sample post data for testing"""
    return {
        "id": 1,
        "text": "Sample post text",
        "topic": "Technology"
    }


@pytest.fixture
def sample_feed_data():
    """Sample feed action data for testing"""
    return {
        "user_id": 123,
        "post_id": 1,
        "action": "like",
        "time": "2024-01-01T12:00:00"
    }


@pytest.fixture
def sample_recommendation_response():
    """Sample recommendation response for testing"""
    return {
        "exp_group": "control",
        "recommendations": [
            {
                "id": 1,
                "text": "Post 1",
                "topic": "Technology"
            },
            {
                "id": 2,
                "text": "Post 2",
                "topic": "Science"
            }
        ]
    }
