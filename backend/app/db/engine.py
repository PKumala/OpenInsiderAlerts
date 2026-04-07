import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def wait_for_db(max_retries: int = 20, delay: int = 3):
    for i in range(max_retries):
        try:
            with engine.connect():
                print("Database connected.")
                return
        except OperationalError:
            print(f"Database not ready, retrying... ({i+1}/{max_retries})")
            time.sleep(delay)

    raise RuntimeError("Database not available after retries.")
