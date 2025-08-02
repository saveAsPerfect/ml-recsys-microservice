import pandas as pd
from sqlalchemy import create_engine
from app.config import DATABASE_URL, CHUNKSIZE
from app.core.logging_config import get_logger
from app.db.database import retry_on_failure
from datetime import datetime

logger = get_logger(__name__)


@retry_on_failure()
def batch_load_sql(query: str) -> pd.DataFrame:
    """Load data from database in chunks with error handling"""
    logger.info(f"Loading data with query: {query[:100]}...")
    engine = create_engine(DATABASE_URL)
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []

    try:
        for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
            chunks.append(chunk_dataframe)
            logger.debug(f"Loaded chunk with {len(chunk_dataframe)} rows")

        result = pd.concat(chunks, ignore_index=True)
        logger.info(f"Successfully loaded {len(result)} total rows")
        return result
    except Exception as e:
        logger.error(f"Error loading data from database: {e}")
        raise
    finally:
        conn.close()
        logger.debug("Database connection closed")


def load_features(query: str) -> pd.DataFrame:
    """Load features from database with logging"""
    logger.info(f"Loading features with query: {query[:100]}...")
    return batch_load_sql(query)


def build_features(user_id: int, post_features: pd.DataFrame, user_features: pd.DataFrame, time: datetime):
    """Build features for recommendation with logging"""
    logger.debug(f"Building features for user {user_id}")

    user_row = user_features[user_features["user_id"] == user_id]
    if user_row.empty:
        logger.warning(
            f"User {user_id} not found in user features - cold start")
        return pd.DataFrame()  # cold start

    df = post_features.merge(user_row, how="cross")
    df["day_of_week"] = time.weekday()
    df["hour"] = time.hour

    logger.debug(
        f"Built features for user {user_id}: {len(df)} post-user combinations")
    return df
