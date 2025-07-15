import pandas as pd
from sqlalchemy import create_engine

from app.core.config import DATABASE_URL

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
