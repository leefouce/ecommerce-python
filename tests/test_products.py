from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_products_returns_mock_products() -> None:
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Classic T-Shirt",
            "description": "A comfortable cotton t-shirt",
            "price": 19.99,
        },
        {
            "id": 2,
            "name": "Running Shoes",
            "description": "Lightweight shoes for everyday running",
            "price": 89.99,
        },
    ]


def test_get_product_detail_returns_product_when_found() -> None:
    response = client.get("/products/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Classic T-Shirt",
        "description": "A comfortable cotton t-shirt",
        "price": 19.99,
    }


def test_get_product_detail_returns_404_when_missing() -> None:
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
