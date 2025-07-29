import pandas as pd
from sqlalchemy import create_engine
from app.config import DATABASE_URL
from datetime import datetime

CHUNKSIZE = 200000

def batch_load_sql(query: str) -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)


def load_features(query: str) -> pd.DataFrame:
    return batch_load_sql(query)


def build_features(user_id: int, post_features: pd.DataFrame, user_features: pd.DataFrame, time: datetime):
    user_row = user_features[user_features["user_id"] == user_id]
    if user_row.empty:
        return pd.DataFrame()  # cold start

    df = post_features.merge(user_row, how="cross")
    df["day_of_week"] = time.weekday()
    df["hour"] = time.hour
    return df
