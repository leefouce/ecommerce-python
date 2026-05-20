from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.product import ProductModel
from app.repositories.products import get_product_by_id, list_products


def test_product_repository_reads_products_from_database() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        db.add(
            ProductModel(
                id=1,
                name="Classic T-Shirt",
                description="A comfortable cotton t-shirt",
                price=19.99,
            )
        )
        db.add(
            ProductModel(
                id=2,
                name="Running Shoes",
                description="Lightweight shoes for everyday running",
                price=89.99,
            )
        )
        db.commit()

        products = list_products(db)
        product = get_product_by_id(db, 1)
        missing_product = get_product_by_id(db, 999)
    finally:
        db.close()

    assert [item.name for item in products] == ["Classic T-Shirt", "Running Shoes"]
    assert product is not None
    assert product.description == "A comfortable cotton t-shirt"
    assert missing_product is None
