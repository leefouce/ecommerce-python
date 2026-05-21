from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.auth as auth_api
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_register_creates_user_without_returning_password_hash(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "buyer@example.com", "password": "correct horse battery staple"},
    )

    assert response.status_code == 201
    assert response.json() == {"id": 1, "email": "buyer@example.com"}


def test_register_returns_400_for_duplicate_email(client: TestClient) -> None:
    payload = {"email": "buyer@example.com", "password": "correct horse battery staple"}

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json() == {"detail": "Email already registered"}


def test_register_returns_400_when_unique_constraint_fails(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_integrity_error(*args: object, **kwargs: object) -> None:
        raise IntegrityError("insert", {}, Exception("unique constraint failed"))

    monkeypatch.setattr(auth_api, "create_user", raise_integrity_error)

    response = client.post(
        "/auth/register",
        json={"email": "buyer@example.com", "password": "correct horse battery staple"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_login_returns_user_when_password_is_correct(client: TestClient) -> None:
    payload = {"email": "buyer@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "email": "buyer@example.com"}


def test_login_returns_401_when_password_is_wrong(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "buyer@example.com", "password": "correct horse battery staple"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "buyer@example.com", "password": "wrong password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}
