import os
from urllib.parse import urlparse

import psycopg2
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app


def _default_test_database_url() -> str:
    parsed = urlparse(settings.DATABASE_URL)
    db_name = parsed.path.lstrip("/") or "swiftval_db"
    test_db_name = f"{db_name}_test"
    return parsed._replace(path=f"/{test_db_name}").geturl()


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", _default_test_database_url())


def _ensure_database_exists(database_url: str) -> None:
    parsed = urlparse(database_url)
    admin_db = parsed._replace(path="/postgres").geturl()
    db_name = parsed.path.lstrip("/")

    conn = psycopg2.connect(admin_db)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        conn.close()


_ensure_database_exists(TEST_DATABASE_URL)

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.rollback()
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE quote_photos, quotes, pricing_rules, partners, vehicles RESTART IDENTITY CASCADE"))
        db_session.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
