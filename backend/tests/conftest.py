import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db import Base
from backend.app.config import settings
from backend.app.models import chase, kyc, governance

TEST_DB_PATH = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    return create_engine(TEST_DB_PATH, connect_args={"check_same_thread": False})

@pytest.fixture(scope="function")
def db_session(engine):
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
