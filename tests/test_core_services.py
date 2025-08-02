import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

from app.core.recommender import RecommenderService
from app.core.model_loader import load_models
from app.core.features import load_features


class TestRecommenderService:
    """Test cases for the RecommenderService"""

    @pytest.fixture
    def mock_model_control(self):
        """Mock control model"""
        model = Mock()
        model.predict.return_value = np.array([0.8, 0.6, 0.9, 0.7, 0.5])
        return model

    @pytest.fixture
    def mock_model_test(self):
        """Mock test model"""
        model = Mock()
        model.predict.return_value = np.array([0.9, 0.7, 0.8, 0.6, 0.8])
        return model

    @pytest.fixture
    def mock_user_features(self):
        """Mock user features DataFrame"""
        return pd.DataFrame({
            'user_id': [1, 2, 3, 4, 5],
            'feature_1': [0.1, 0.2, 0.3, 0.4, 0.5],
            'feature_2': [0.6, 0.7, 0.8, 0.9, 1.0]
        }).set_index('user_id')

    @pytest.fixture
    def mock_post_features(self):
        """Mock post features DataFrame"""
        return pd.DataFrame({
            'post_id': [1, 2, 3, 4, 5],
            'feature_1': [0.1, 0.2, 0.3, 0.4, 0.5],
            'feature_2': [0.6, 0.7, 0.8, 0.9, 1.0]
        }).set_index('post_id')

    @pytest.fixture
    def recommender_service(self, mock_model_control, mock_model_test, mock_user_features, mock_post_features):
        """RecommenderService instance with mocked dependencies"""
        return RecommenderService(
            model_control=mock_model_control,
            model_test=mock_model_test,
            user_features=mock_user_features,
            post_features=mock_post_features
        )

    def test_recommend_control_group(self, recommender_service, mock_model_control):
        """Test recommendation with control group"""
        # Arrange
        user_id = 1
        time = "2024-01-01T12:00:00"
        liked_post_ids = [1, 2]
        limit = 3

        # Mock random choice to return control group
        with patch('app.core.recommender.random.choice', return_value='control'):
            # Act
            recommendations, exp_group = recommender_service.recommend(
                user_id, time, liked_post_ids, limit
            )

        # Assert
        assert exp_group == "control"
        assert len(recommendations) == 3
        mock_model_control.predict.assert_called_once()

    def test_recommend_test_group(self, recommender_service, mock_model_test):
        """Test recommendation with test group"""
        # Arrange
        user_id = 1
        time = "2024-01-01T12:00:00"
        liked_post_ids = [1, 2]
        limit = 3

        # Mock random choice to return test group
        with patch('app.core.recommender.random.choice', return_value='test'):
            # Act
            recommendations, exp_group = recommender_service.recommend(
                user_id, time, liked_post_ids, limit
            )

        # Assert
        assert exp_group == "test"
        assert len(recommendations) == 3
        mock_model_test.predict.assert_called_once()

    def test_recommend_user_not_found(self, recommender_service):
        """Test recommendation when user is not found in features"""
        # Arrange
        user_id = 999  # User not in mock_user_features
        time = "2024-01-01T12:00:00"
        liked_post_ids = [1, 2]
        limit = 3

        # Act & Assert
        with pytest.raises(KeyError):
            recommender_service.recommend(user_id, time, liked_post_ids, limit)

    def test_recommend_empty_liked_posts(self, recommender_service, mock_model_control):
        """Test recommendation with empty liked posts list"""
        # Arrange
        user_id = 1
        time = "2024-01-01T12:00:00"
        liked_post_ids = []
        limit = 3

        # Mock random choice to return control group
        with patch('app.core.recommender.random.choice', return_value='control'):
            # Act
            recommendations, exp_group = recommender_service.recommend(
                user_id, time, liked_post_ids, limit
            )

        # Assert
        assert exp_group == "control"
        assert len(recommendations) == 3
        mock_model_control.predict.assert_called_once()

    def test_recommend_custom_limit(self, recommender_service, mock_model_control):
        """Test recommendation with custom limit"""
        # Arrange
        user_id = 1
        time = "2024-01-01T12:00:00"
        liked_post_ids = [1, 2]
        limit = 5

        # Mock random choice to return control group
        with patch('app.core.recommender.random.choice', return_value='control'):
            # Act
            recommendations, exp_group = recommender_service.recommend(
                user_id, time, liked_post_ids, limit
            )

        # Assert
        assert exp_group == "control"
        assert len(recommendations) == 5
        mock_model_control.predict.assert_called_once()

    def test_recommend_model_prediction_error(self, recommender_service, mock_model_control):
        """Test recommendation when model prediction fails"""
        # Arrange
        user_id = 1
        time = "2024-01-01T12:00:00"
        liked_post_ids = [1, 2]
        limit = 3

        # Mock model to raise exception
        mock_model_control.predict.side_effect = Exception(
            "Model prediction error")

        # Mock random choice to return control group
        with patch('app.core.recommender.random.choice', return_value='control'):
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                recommender_service.recommend(
                    user_id, time, liked_post_ids, limit)

            assert "Model prediction error" in str(exc_info.value)


class TestModelLoader:
    """Test cases for the model loader"""

    @patch('app.core.model_loader.joblib.load')
    def test_load_models_success(self, mock_joblib_load):
        """Test successful model loading"""
        # Arrange
        mock_model = Mock()
        mock_joblib_load.return_value = mock_model

        # Act
        model_control, model_test = load_models()

        # Assert
        assert model_control == mock_model
        assert model_test == mock_model
        assert mock_joblib_load.call_count == 2

    @patch('app.core.model_loader.joblib.load')
    def test_load_models_file_not_found(self, mock_joblib_load):
        """Test model loading when file is not found"""
        # Arrange
        mock_joblib_load.side_effect = FileNotFoundError(
            "Model file not found")

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            load_models()

        assert "Model file not found" in str(exc_info.value)


class TestFeaturesLoader:
    """Test cases for the features loader"""

    @patch('app.core.features.pd.read_sql')
    @patch('app.core.features.create_engine')
    def test_load_features_success(self, mock_create_engine, mock_read_sql):
        """Test successful features loading"""
        # Arrange
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        mock_df = pd.DataFrame({
            'id': [1, 2, 3],
            'feature_1': [0.1, 0.2, 0.3],
            'feature_2': [0.4, 0.5, 0.6]
        })
        mock_read_sql.return_value = mock_df

        query = "SELECT * FROM test_table"

        # Act
        result = load_features(query)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        mock_create_engine.assert_called_once()
        mock_read_sql.assert_called_once_with(query, mock_engine)

    @patch('app.core.features.pd.read_sql')
    @patch('app.core.features.create_engine')
    def test_load_features_database_error(self, mock_create_engine, mock_read_sql):
        """Test features loading when database error occurs"""
        # Arrange
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        mock_read_sql.side_effect = Exception("Database connection error")

        query = "SELECT * FROM test_table"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            load_features(query)

        assert "Database connection error" in str(exc_info.value)

    @patch('app.core.features.pd.read_sql')
    @patch('app.core.features.create_engine')
    def test_load_features_empty_result(self, mock_create_engine, mock_read_sql):
        """Test features loading with empty result"""
        # Arrange
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        mock_df = pd.DataFrame()  # Empty DataFrame
        mock_read_sql.return_value = mock_df

        query = "SELECT * FROM empty_table"

        # Act
        result = load_features(query)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
