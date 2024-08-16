import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

LLM_DATABASE_URL = os.getenv("LLM_DATABASE_URL")
LLM_DATABASE_ADMIN_USER = os.getenv("LLM_DATABASE_ADMIN_USER")
LLM_DATABASE_PASSWORD = os.getenv("LLM_DATABASE_PASSWORD")
LLM_DATABASE_DB = os.getenv("LLM_DATABASE_DB")

if not LLM_DATABASE_URL:
    raise ValueError("LLM_DATABASE_URL is not set")
if not LLM_DATABASE_ADMIN_USER:
    raise ValueError("LLM_DATABASE_ADMIN_USER is not set")
if not LLM_DATABASE_PASSWORD:
    raise ValueError("LLM_DATABASE_PASSWORD is not set")
if not LLM_DATABASE_DB:
    raise ValueError("LLM_DATABASE_DB is not set")

DATABASE_SQL_ALCHEMY = (
    f"postgresql://{LLM_DATABASE_ADMIN_USER}:{LLM_DATABASE_PASSWORD}@{LLM_DATABASE_URL}/{LLM_DATABASE_DB}"
)

logger.info(f"Connecting to database at {DATABASE_SQL_ALCHEMY}")

engine = create_engine(DATABASE_SQL_ALCHEMY)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
