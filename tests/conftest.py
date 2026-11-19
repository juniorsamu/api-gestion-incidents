import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app, get_db


engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionTest = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)


def get_db_test():
    db = SessionTest()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def base_de_donnees_de_test():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    app.dependency_overrides[get_db] = get_db_test

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)