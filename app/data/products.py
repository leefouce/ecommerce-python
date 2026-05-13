from app.schemas.product import Product

MOCK_PRODUCTS: list[Product] = [
    Product(
        id=1,
        name="Classic T-Shirt",
        description="A comfortable cotton t-shirt",
        price=19.99,
    ),
    Product(
        id=2,
        name="Running Shoes",
        description="Lightweight shoes for everyday running",
        price=89.99,
    ),
]


def list_products() -> list[Product]:
    return MOCK_PRODUCTS


def get_product_by_id(product_id: int) -> Product | None:
    return next((product for product in MOCK_PRODUCTS if product.id == product_id), None)
