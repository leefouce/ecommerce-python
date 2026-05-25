from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.models.cart import CartItemModel
from app.models.order import OrderItemModel, OrderModel
from app.models.product import ProductModel
from app.models.user import UserModel

# Import models so SQLAlchemy registers their tables before create_all runs.
_ = (CartItemModel, OrderItemModel, OrderModel, UserModel)


def _ensure_user_admin_column() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "is_admin" in user_columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0")
        )


SEED_PRODUCTS = [
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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_user_admin_column()

    with Session(engine) as db:
        if db.query(ProductModel).first() is not None:
            return

        db.add_all(ProductModel(**product) for product in SEED_PRODUCTS)
        db.commit()
