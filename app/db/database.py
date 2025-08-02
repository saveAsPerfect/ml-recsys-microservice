from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import (
    DATABASE_URL,
    DB_POOL_SIZE,
    DB_MAX_OVERFLOW,
    DB_POOL_TIMEOUT,
    DB_POOL_RECYCLE,
    MAX_RETRIES,
    RETRY_DELAY
)
from app.core.logging_config import get_logger
import time
from functools import wraps

logger = get_logger(__name__)

# Create engine with connection pool settings
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before use
    echo=False  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(bind=engine)


def retry_on_failure(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """Decorator for retrying database operations on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        time.sleep(delay * (2 ** attempt))
            logger.error(
                f"Database operation failed after {max_retries} attempts: {last_exception}")
            raise last_exception
        return wrapper
    return decorator


def get_db():
    """Get database session with connection logging"""
    db = SessionLocal()
    try:
        logger.debug("Database connection established")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Database connection closed")
        db.close()


@retry_on_failure()
def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
