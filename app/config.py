from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Model configuration
MODEL_CONTROL_PATH = os.getenv("MODEL_CONTROL_PATH")
MODEL_TEST_PATH = os.getenv("MODEL_TEST_PATH")
if not MODEL_CONTROL_PATH or not MODEL_TEST_PATH:
    raise ValueError(
        "MODEL_CONTROL_PATH and MODEL_TEST_PATH environment variables are required")

# Feature loading configuration
CHUNKSIZE = int(os.getenv("CHUNKSIZE", "200000"))

# SQL Queries for feature loading
USER_FEATURES_QUERY = os.getenv(
    "USER_FEATURES_QUERY",
    "SELECT * FROM public.user_data"
)
POST_FEATURES_QUERY = os.getenv(
    "POST_FEATURES_QUERY",
    "SELECT * FROM public.post_text_df"
)

# AB Testing configuration
AB_TEST_ENABLED = os.getenv("AB_TEST_ENABLED", "False").lower() == "true"
SALT = os.getenv("SALT", "salt")
GROUP_A_PERCENTAGE = int(os.getenv("GROUP_A_PERCENTAGE", "50"))

# Database pool configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Retry configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv(
    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
