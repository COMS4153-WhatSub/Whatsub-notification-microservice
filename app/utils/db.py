from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator, Callable
from app.utils.settings import get_settings

Base = declarative_base()
settings = get_settings()

def get_db_url() -> str:
    return f"mysql+pymysql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

def get_engine():
    return create_engine(get_db_url(), pool_pre_ping=True)

def get_session_factory() -> Callable[[], Session]:
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_all(engine):
    Base.metadata.create_all(bind=engine)

