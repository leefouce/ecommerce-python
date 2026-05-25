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


def test_checkout_creates_order_from_cart_and_clears_cart(client: TestClient) -> None:
    headers = _auth_headers(client)
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=headers,
    )

    checkout_response = client.post("/orders/checkout", headers=headers)
    cart_response = client.get("/cart/items", headers=headers)

    assert checkout_response.status_code == 201
    assert checkout_response.json() == {
        "id": 1,
        "status": "created",
        "items": [{"product_id": 1, "quantity": 2}],
    }
    assert cart_response.status_code == 200
    assert cart_response.json() == []


def test_authenticated_user_can_list_their_order_history(client: TestClient) -> None:
    headers = _auth_headers(client)
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=headers,
    )
    client.post("/orders/checkout", headers=headers)

    response = client.get("/orders", headers=headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "status": "created",
            "items": [{"product_id": 1, "quantity": 2}],
        }
    ]


def test_order_history_is_isolated_between_users(client: TestClient) -> None:
    buyer_headers = _auth_headers(client, "buyer@example.com")
    other_buyer_headers = _auth_headers(client, "other-buyer@example.com")
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers=buyer_headers,
    )
    client.post("/orders/checkout", headers=buyer_headers)

    response = client.get("/orders", headers=other_buyer_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_order_endpoints_require_authentication(client: TestClient) -> None:
    checkout_response = client.post("/orders/checkout")
    history_response = client.get("/orders")

    assert checkout_response.status_code == 401
    assert checkout_response.json() == {"detail": "Not authenticated"}
    assert history_response.status_code == 401
    assert history_response.json() == {"detail": "Not authenticated"}
