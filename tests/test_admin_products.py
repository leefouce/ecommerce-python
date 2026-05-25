from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.product import ProductModel
from app.models.user import UserModel
from app.security.passwords import hash_password


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add_all(
            [
                ProductModel(
                    id=1,
                    name="Classic T-Shirt",
                    description="A comfortable cotton t-shirt",
                    price=19.99,
                ),
                UserModel(
                    email="admin@example.com",
                    password_hash=hash_password("correct horse battery staple"),
                    is_admin=True,
                ),
                UserModel(
                    email="buyer@example.com",
                    password_hash=hash_password("correct horse battery staple"),
                    is_admin=False,
                ),
            ]
        )
        db.commit()

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


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    payload = {"email": email, "password": "correct horse battery staple"}
    login_response = client.post("/auth/login", json=payload)
    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_admin_can_create_product(client: TestClient) -> None:
    response = client.post(
        "/admin/products",
        json={
            "name": "Water Bottle",
            "description": "Reusable stainless bottle",
            "price": 12.5,
        },
        headers=_auth_headers(client, "admin@example.com"),
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "name": "Water Bottle",
        "description": "Reusable stainless bottle",
        "price": 12.5,
    }


def test_admin_can_update_product(client: TestClient) -> None:
    response = client.patch(
        "/admin/products/1",
        json={"name": "Premium T-Shirt", "price": 24.99},
        headers=_auth_headers(client, "admin@example.com"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Premium T-Shirt",
        "description": "A comfortable cotton t-shirt",
        "price": 24.99,
    }


def test_admin_can_delete_product(client: TestClient) -> None:
    delete_response = client.delete(
        "/admin/products/1",
        headers=_auth_headers(client, "admin@example.com"),
    )
    detail_response = client.get("/products/1")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert detail_response.status_code == 404


@pytest.mark.parametrize(
    ("method", "path", "json"),
    [
        (
            "post",
            "/admin/products",
            {"name": "Hat", "description": "Cotton hat", "price": 9.99},
        ),
        ("patch", "/admin/products/1", {"name": "Updated Shirt"}),
        ("delete", "/admin/products/1", None),
    ],
)
def test_admin_product_endpoints_require_authentication(
    client: TestClient,
    method: str,
    path: str,
    json: dict[str, str | float] | None,
) -> None:
    response = client.request(method, path, json=json)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    ("method", "path", "json"),
    [
        (
            "post",
            "/admin/products",
            {"name": "Hat", "description": "Cotton hat", "price": 9.99},
        ),
        ("patch", "/admin/products/1", {"name": "Updated Shirt"}),
        ("delete", "/admin/products/1", None),
    ],
)
def test_admin_product_endpoints_reject_non_admin_users(
    client: TestClient,
    method: str,
    path: str,
    json: dict[str, str | float] | None,
) -> None:
    response = client.request(
        method,
        path,
        json=json,
        headers=_auth_headers(client, "buyer@example.com"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_update_missing_product_returns_404(client: TestClient) -> None:
    response = client.patch(
        "/admin/products/999",
        json={"name": "Missing"},
        headers=_auth_headers(client, "admin@example.com"),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_delete_missing_product_returns_404(client: TestClient) -> None:
    response = client.delete(
        "/admin/products/999",
        headers=_auth_headers(client, "admin@example.com"),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
