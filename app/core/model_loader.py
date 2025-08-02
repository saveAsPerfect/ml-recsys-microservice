from catboost import CatBoostRanker
from app.config import MODEL_CONTROL_PATH, MODEL_TEST_PATH
from app.core.logging_config import get_logger
import os

logger = get_logger(__name__)


def load_models():
    """Load ML models with error handling and logging"""
    logger.info("Starting model loading process")

    # Check if model files exist
    if not os.path.exists(MODEL_CONTROL_PATH):
        raise FileNotFoundError(
            f"Control model file not found: {MODEL_CONTROL_PATH}")
    if not os.path.exists(MODEL_TEST_PATH):
        raise FileNotFoundError(
            f"Test model file not found: {MODEL_TEST_PATH}")

    try:
        logger.info(f"Loading control model from {MODEL_CONTROL_PATH}")
        model_control = CatBoostRanker()
        model_control.load_model(MODEL_CONTROL_PATH)
        logger.info("Control model loaded successfully")

        logger.info(f"Loading test model from {MODEL_TEST_PATH}")
        model_test = CatBoostRanker()
        model_test.load_model(MODEL_TEST_PATH)
        logger.info("Test model loaded successfully")

        logger.info("All models loaded successfully")
        return model_control, model_test

    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise


# Global variables for models (will be initialized in startup event)
model_control = None
model_test = None
