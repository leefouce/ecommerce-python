from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import ProductModel


def list_products(db: Session) -> list[ProductModel]:
    statement = select(ProductModel).order_by(ProductModel.id)
    return list(db.scalars(statement).all())


def get_product_by_id(db: Session, product_id: int) -> ProductModel | None:
    statement = select(ProductModel).where(ProductModel.id == product_id)
    return db.scalar(statement)


def create_product(
    db: Session,
    *,
    name: str,
    description: str,
    price: float,
) -> ProductModel:
    product = ProductModel(name=name, description=description, price=price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(
    db: Session,
    product: ProductModel,
    *,
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
) -> ProductModel:
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: ProductModel) -> None:
    db.delete(product)
    db.commit()
