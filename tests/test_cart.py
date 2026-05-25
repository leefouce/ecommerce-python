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
        db.add(
            ProductModel(
                id=1,
                name="Classic T-Shirt",
                description="A comfortable cotton t-shirt",
                price=19.99,
            )
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


def _auth_headers(client: TestClient, email: str = "buyer@example.com") -> dict[str, str]:
    payload = {"email": email, "password": "correct horse battery staple"}
    client.post("/auth/register", json=payload)
    login_response = client.post("/auth/login", json=payload)
    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_authenticated_user_can_add_product_to_cart(client: TestClient) -> None:
    response = client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=_auth_headers(client),
    )

    assert response.status_code == 201
    assert response.json() == {"product_id": 1, "quantity": 2}


def test_authenticated_user_can_list_cart_items(client: TestClient) -> None:
    headers = _auth_headers(client)
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=headers,
    )

    response = client.get("/cart/items", headers=headers)

    assert response.status_code == 200
    assert response.json() == [{"product_id": 1, "quantity": 2}]


def test_cart_items_are_isolated_between_users(client: TestClient) -> None:
    buyer_headers = _auth_headers(client, "buyer@example.com")
    other_buyer_headers = _auth_headers(client, "other-buyer@example.com")
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=buyer_headers,
    )

    response = client.get("/cart/items", headers=other_buyer_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_authenticated_user_can_remove_product_from_cart(client: TestClient) -> None:
    headers = _auth_headers(client)
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=headers,
    )

    delete_response = client.delete("/cart/items/1", headers=headers)
    list_response = client.get("/cart/items", headers=headers)

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.parametrize(
    ("method", "path", "json"),
    [
        ("post", "/cart/items", {"product_id": 1, "quantity": 1}),
        ("get", "/cart/items", None),
        ("delete", "/cart/items/1", None),
    ],
)
def test_cart_endpoints_require_authentication(
    client: TestClient,
    method: str,
    path: str,
    json: dict[str, int] | None,
) -> None:
    response = client.request(method, path, json=json)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_add_cart_item_returns_404_when_product_does_not_exist(
    client: TestClient,
) -> None:
    response = client.post(
        "/cart/items",
        json={"product_id": 999, "quantity": 1},
        headers=_auth_headers(client),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


@pytest.mark.parametrize("quantity", [0, -1])
def test_add_cart_item_rejects_non_positive_quantity(
    client: TestClient,
    quantity: int,
) -> None:
    response = client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": quantity},
        headers=_auth_headers(client),
    )

    assert response.status_code == 422


def test_user_cannot_delete_another_users_cart_item(client: TestClient) -> None:
    buyer_headers = _auth_headers(client, "buyer@example.com")
    other_buyer_headers = _auth_headers(client, "other-buyer@example.com")
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=buyer_headers,
    )

    delete_response = client.delete("/cart/items/1", headers=other_buyer_headers)
    buyer_cart_response = client.get("/cart/items", headers=buyer_headers)

    assert delete_response.status_code == 204
    assert buyer_cart_response.status_code == 200
    assert buyer_cart_response.json() == [{"product_id": 1, "quantity": 2}]
