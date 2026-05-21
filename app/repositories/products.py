from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import ProductModel


def list_products(db: Session) -> list[ProductModel]:
    statement = select(ProductModel).order_by(ProductModel.id)
    return list(db.scalars(statement).all())


def get_product_by_id(db: Session, product_id: int) -> ProductModel | None:
    statement = select(ProductModel).where(ProductModel.id == product_id)
    return db.scalar(statement)
