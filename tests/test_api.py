import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.models.models import Post


class TestRecommendationsAPI:
    """Test cases for the recommendations API endpoint"""

    def test_recommendations_success(self, client, override_get_db):
        """Test successful API call to recommendations endpoint"""
        # Arrange
        mock_db = override_get_db
        user_id = 123
        time = "2024-01-01T12:00:00"
        limit = 5

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = [
            (1,), (2,), (3,)
        ]
        mock_db.query.return_value = mock_query

        # Mock recommender service
        with patch('app.api.recommendations.recommender_service') as mock_service:
            mock_service.recommend.return_value = ([4, 5, 6, 7, 8], "control")

            # Mock database query for posts
            mock_post_query = Mock()
            mock_post_query.filter.return_value.all.return_value = [
                Post(id=4, text="Post 4", topic="Technology"),
                Post(id=5, text="Post 5", topic="Science"),
                Post(id=6, text="Post 6", topic="Health"),
                Post(id=7, text="Post 7", topic="Sports"),
                Post(id=8, text="Post 8", topic="Politics")
            ]
            mock_db.query.return_value = mock_post_query

            # Act
            response = client.get(
                f"/post/recommendations/?user_id={user_id}&time={time}&limit={limit}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["exp_group"] == "control"
        assert len(data["recommendations"]) == 5
        assert data["recommendations"][0]["id"] == 4
        assert data["recommendations"][0]["text"] == "Post 4"
        assert data["recommendations"][0]["topic"] == "Technology"

    def test_recommendations_user_not_found(self, client, override_get_db):
        """Test API call when user is not found"""
        # Arrange
        mock_db = override_get_db
        user_id = 999
        time = "2024-01-01T12:00:00"
        limit = 5

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Mock recommender service to raise KeyError
        with patch('app.api.recommendations.recommender_service') as mock_service:
            mock_service.recommend.side_effect = KeyError("User not found")

            # Act
            response = client.get(
                f"/post/recommendations/?user_id={user_id}&time={time}&limit={limit}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == f"User {user_id} not found"

    def test_recommendations_missing_parameters(self, client):
        """Test API call with missing required parameters"""
        # Act
        response = client.get("/post/recommendations/")

        # Assert
        assert response.status_code == 422  # Validation error

    def test_recommendations_invalid_user_id(self, client):
        """Test API call with invalid user_id parameter"""
        # Act
        response = client.get(
            "/post/recommendations/?user_id=invalid&time=2024-01-01T12:00:00")

        # Assert
        assert response.status_code == 422  # Validation error

    def test_recommendations_invalid_time_format(self, client):
        """Test API call with invalid time format"""
        # Act
        response = client.get(
            "/post/recommendations/?user_id=123&time=invalid-time&limit=5")

        # Assert
        assert response.status_code == 422  # Validation error

    def test_recommendations_custom_limit(self, client, override_get_db):
        """Test API call with custom limit parameter"""
        # Arrange
        mock_db = override_get_db
        user_id = 123
        time = "2024-01-01T12:00:00"
        limit = 3

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = [
            (1,), (2,), (3,)
        ]
        mock_db.query.return_value = mock_query

        # Mock recommender service
        with patch('app.api.recommendations.recommender_service') as mock_service:
            mock_service.recommend.return_value = ([4, 5, 6], "test")

            # Mock database query for posts
            mock_post_query = Mock()
            mock_post_query.filter.return_value.all.return_value = [
                Post(id=4, text="Post 4", topic="Technology"),
                Post(id=5, text="Post 5", topic="Science"),
                Post(id=6, text="Post 6", topic="Health")
            ]
            mock_db.query.return_value = mock_post_query

            # Act
            response = client.get(
                f"/post/recommendations/?user_id={user_id}&time={time}&limit={limit}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["exp_group"] == "test"
        assert len(data["recommendations"]) == 3

    def test_recommendations_empty_recommendations(self, client, override_get_db):
        """Test API call when no recommendations are returned"""
        # Arrange
        mock_db = override_get_db
        user_id = 123
        time = "2024-01-01T12:00:00"
        limit = 5

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Mock recommender service
        with patch('app.api.recommendations.recommender_service') as mock_service:
            mock_service.recommend.return_value = ([], "control")

            # Mock database query for posts
            mock_post_query = Mock()
            mock_post_query.filter.return_value.all.return_value = []
            mock_db.query.return_value = mock_post_query

            # Act
            response = client.get(
                f"/post/recommendations/?user_id={user_id}&time={time}&limit={limit}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["exp_group"] == "control"
        assert len(data["recommendations"]) == 0

    def test_recommendations_database_error(self, client, override_get_db):
        """Test API call when database error occurs"""
        # Arrange
        mock_db = override_get_db
        user_id = 123
        time = "2024-01-01T12:00:00"
        limit = 5

        # Mock database to raise an exception
        mock_db.query.side_effect = Exception("Database connection error")

        # Act
        response = client.get(
            f"/post/recommendations/?user_id={user_id}&time={time}&limit={limit}")

        # Assert
        assert response.status_code == 500  # Internal server error

    def test_recommendations_recommender_service_error(self, client, override_get_db):
        """Test API call when recommender service error occurs"""
        # Arrange
        mock_db = override_get_db
        user_id = 123
        time = "2024-01-01T12:00:00"
        limit = 5

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Mock recommender service to raise an exception
        with patch('app.api.recommendations.recommender_service') as mock_service:
            mock_service.recommend.side_effect = Exception(
                "Model loading error")

            # Act
            response = client.get(
                f"/post/recommendations/?user_id={user_id}&time={time}&limit={limit}")

        # Assert
        assert response.status_code == 500  # Internal server error

    def test_recommendations_different_experiment_groups(self, client, override_get_db):
        """Test API call with different experiment groups"""
        # Arrange
        mock_db = override_get_db
        user_id = 123
        time = "2024-01-01T12:00:00"
        limit = 5
        test_exp_groups = ["control", "test", "variant_a", "variant_b"]

        for exp_group in test_exp_groups:
            # Mock database query for liked posts
            mock_query = Mock()
            mock_query.filter.return_value.distinct.return_value.all.return_value = [
                (1,), (2,), (3,)
            ]
            mock_db.query.return_value = mock_query

            # Mock recommender service
            with patch('app.api.recommendations.recommender_service') as mock_service:
                mock_service.recommend.return_value = (
                    [4, 5, 6, 7, 8], exp_group)

                # Mock database query for posts
                mock_post_query = Mock()
                mock_post_query.filter.return_value.all.return_value = [
                    Post(id=4, text="Post 4", topic="Technology"),
                    Post(id=5, text="Post 5", topic="Science"),
                    Post(id=6, text="Post 6", topic="Health"),
                    Post(id=7, text="Post 7", topic="Sports"),
                    Post(id=8, text="Post 8", topic="Politics")
                ]
                mock_db.query.return_value = mock_post_query

                # Act
                response = client.get(
                    f"/post/recommendations/?user_id={user_id}&time={time}&limit={limit}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["exp_group"] == exp_group
            assert len(data["recommendations"]) == 5

    def test_recommendations_default_limit(self, client, override_get_db):
        """Test API call with default limit (5)"""
        # Arrange
        mock_db = override_get_db
        user_id = 123
        time = "2024-01-01T12:00:00"

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Mock recommender service
        with patch('app.api.recommendations.recommender_service') as mock_service:
            mock_service.recommend.return_value = ([4, 5, 6, 7, 8], "control")

            # Mock database query for posts
            mock_post_query = Mock()
            mock_post_query.filter.return_value.all.return_value = [
                Post(id=4, text="Post 4", topic="Technology"),
                Post(id=5, text="Post 5", topic="Science"),
                Post(id=6, text="Post 6", topic="Health"),
                Post(id=7, text="Post 7", topic="Sports"),
                Post(id=8, text="Post 8", topic="Politics")
            ]
            mock_db.query.return_value = mock_post_query

            # Act
            response = client.get(
                f"/post/recommendations/?user_id={user_id}&time={time}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) == 5  # Default limit
