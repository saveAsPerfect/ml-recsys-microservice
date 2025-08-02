import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from app.api.recommendations import recommended_posts
from app.models.models import Post, Feed
from app.schemas.schemas import Response


class TestRecommendedPostsHandler:
    """Test cases for the recommended_posts handler"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_recommender_service(self):
        """Mock recommender service"""
        with patch('app.api.recommendations.recommender_service') as mock_service:
            yield mock_service

    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing"""
        return 123

    @pytest.fixture
    def sample_time(self):
        """Sample datetime for testing"""
        return datetime(2024, 1, 1, 12, 0, 0)

    @pytest.fixture
    def sample_liked_posts(self):
        """Sample liked post IDs"""
        return [1, 2, 3]

    @pytest.fixture
    def sample_recommendations(self):
        """Sample recommended post IDs"""
        return [4, 5, 6, 7, 8]

    @pytest.fixture
    def sample_posts(self):
        """Sample Post objects"""
        return [
            Post(id=4, text="Post 4", topic="Technology"),
            Post(id=5, text="Post 5", topic="Science"),
            Post(id=6, text="Post 6", topic="Health"),
            Post(id=7, text="Post 7", topic="Sports"),
            Post(id=8, text="Post 8", topic="Politics")
        ]

    def test_recommended_posts_success(
        self,
        mock_db,
        mock_recommender_service,
        sample_user_id,
        sample_time,
        sample_liked_posts,
        sample_recommendations,
        sample_posts
    ):
        """Test successful recommendation retrieval"""
        # Arrange
        limit = 5
        exp_group = "control"

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = [
            (1,), (2,), (3,)
        ]
        mock_db.query.return_value = mock_query

        # Mock recommender service
        mock_recommender_service.recommend.return_value = (
            sample_recommendations, exp_group)

        # Mock database query for posts
        mock_post_query = Mock()
        mock_post_query.filter.return_value.all.return_value = sample_posts
        mock_db.query.return_value = mock_post_query

        # Act
        result = recommended_posts(sample_user_id, sample_time, limit, mock_db)

        # Assert
        assert isinstance(result, Response)
        assert result.exp_group == exp_group
        assert len(result.recommendations) == 5
        assert result.recommendations[0].id == 4
        assert result.recommendations[0].text == "Post 4"
        assert result.recommendations[0].topic == "Technology"

        # Verify database calls
        mock_db.query.assert_called()
        mock_recommender_service.recommend.assert_called_once_with(
            sample_user_id, sample_time, sample_liked_posts, limit
        )

    def test_recommended_posts_user_not_found(
        self,
        mock_db,
        mock_recommender_service,
        sample_user_id,
        sample_time
    ):
        """Test handling when user is not found"""
        # Arrange
        limit = 5

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Mock recommender service to raise KeyError
        mock_recommender_service.recommend.side_effect = KeyError(
            "User not found")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            recommended_posts(sample_user_id, sample_time, limit, mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == f"User {sample_user_id} not found"

    def test_recommended_posts_no_liked_posts(
        self,
        mock_db,
        mock_recommender_service,
        sample_user_id,
        sample_time,
        sample_recommendations
    ):
        """Test when user has no liked posts"""
        # Arrange
        limit = 5
        exp_group = "test"

        # Mock database query for liked posts (empty)
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Mock recommender service
        mock_recommender_service.recommend.return_value = (
            sample_recommendations, exp_group)

        # Mock database query for posts
        mock_post_query = Mock()
        mock_post_query.filter.return_value.all.return_value = []
        mock_db.query.return_value = mock_post_query

        # Act
        result = recommended_posts(sample_user_id, sample_time, limit, mock_db)

        # Assert
        assert isinstance(result, Response)
        assert result.exp_group == exp_group
        assert len(result.recommendations) == 0

        # Verify recommender service called with empty liked posts list
        mock_recommender_service.recommend.assert_called_once_with(
            sample_user_id, sample_time, [], limit
        )

    def test_recommended_posts_custom_limit(
        self,
        mock_db,
        mock_recommender_service,
        sample_user_id,
        sample_time,
        sample_liked_posts,
        sample_recommendations,
        sample_posts
    ):
        """Test with custom limit parameter"""
        # Arrange
        limit = 3
        exp_group = "control"

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = [
            (1,), (2,), (3,)
        ]
        mock_db.query.return_value = mock_query

        # Mock recommender service
        mock_recommender_service.recommend.return_value = (
            sample_recommendations[:3], exp_group)

        # Mock database query for posts
        mock_post_query = Mock()
        mock_post_query.filter.return_value.all.return_value = sample_posts[:3]
        mock_db.query.return_value = mock_post_query

        # Act
        result = recommended_posts(sample_user_id, sample_time, limit, mock_db)

        # Assert
        assert isinstance(result, Response)
        assert result.exp_group == exp_group
        assert len(result.recommendations) == 3

        # Verify recommender service called with correct limit
        mock_recommender_service.recommend.assert_called_once_with(
            sample_user_id, sample_time, sample_liked_posts, limit
        )

    def test_recommended_posts_database_error(
        self,
        mock_db,
        sample_user_id,
        sample_time
    ):
        """Test handling of database errors"""
        # Arrange
        limit = 5

        # Mock database to raise an exception
        mock_db.query.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            recommended_posts(sample_user_id, sample_time, limit, mock_db)

        assert "Database connection error" in str(exc_info.value)

    def test_recommended_posts_recommender_service_error(
        self,
        mock_db,
        mock_recommender_service,
        sample_user_id,
        sample_time
    ):
        """Test handling of recommender service errors"""
        # Arrange
        limit = 5

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Mock recommender service to raise an exception
        mock_recommender_service.recommend.side_effect = Exception(
            "Model loading error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            recommended_posts(sample_user_id, sample_time, limit, mock_db)

        assert "Model loading error" in str(exc_info.value)

    def test_recommended_posts_empty_recommendations(
        self,
        mock_db,
        mock_recommender_service,
        sample_user_id,
        sample_time,
        sample_liked_posts
    ):
        """Test when recommender service returns empty recommendations"""
        # Arrange
        limit = 5
        exp_group = "control"

        # Mock database query for liked posts
        mock_query = Mock()
        mock_query.filter.return_value.distinct.return_value.all.return_value = [
            (1,), (2,), (3,)
        ]
        mock_db.query.return_value = mock_query

        # Mock recommender service to return empty recommendations
        mock_recommender_service.recommend.return_value = ([], exp_group)

        # Mock database query for posts
        mock_post_query = Mock()
        mock_post_query.filter.return_value.all.return_value = []
        mock_db.query.return_value = mock_post_query

        # Act
        result = recommended_posts(sample_user_id, sample_time, limit, mock_db)

        # Assert
        assert isinstance(result, Response)
        assert result.exp_group == exp_group
        assert len(result.recommendations) == 0

    def test_recommended_posts_different_experiment_groups(
        self,
        mock_db,
        mock_recommender_service,
        sample_user_id,
        sample_time,
        sample_liked_posts,
        sample_recommendations,
        sample_posts
    ):
        """Test different experiment groups"""
        # Arrange
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
            mock_recommender_service.recommend.return_value = (
                sample_recommendations, exp_group)

            # Mock database query for posts
            mock_post_query = Mock()
            mock_post_query.filter.return_value.all.return_value = sample_posts
            mock_db.query.return_value = mock_post_query

            # Act
            result = recommended_posts(
                sample_user_id, sample_time, limit, mock_db)

            # Assert
            assert isinstance(result, Response)
            assert result.exp_group == exp_group
            assert len(result.recommendations) == 5

            # Reset mocks for next iteration
            mock_db.reset_mock()
            mock_recommender_service.reset_mock()
