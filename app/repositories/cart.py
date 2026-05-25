from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import CartItemModel


def list_cart_items(db: Session, *, user_id: int) -> list[CartItemModel]:
    statement = (
        select(CartItemModel)
        .where(CartItemModel.user_id == user_id)
        .order_by(CartItemModel.id)
    )
    return list(db.scalars(statement).all())


def get_cart_item(
    db: Session,
    *,
    user_id: int,
    product_id: int,
) -> CartItemModel | None:
    statement = select(CartItemModel).where(
        CartItemModel.user_id == user_id,
        CartItemModel.product_id == product_id,
    )
    return db.scalar(statement)


def add_cart_item(
    db: Session,
    *,
    user_id: int,
    product_id: int,
    quantity: int,
) -> CartItemModel:
    cart_item = get_cart_item(db, user_id=user_id, product_id=product_id)
    if cart_item is None:
        cart_item = CartItemModel(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(cart_item)
    else:
        cart_item.quantity += quantity

    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_cart_item(db: Session, *, user_id: int, product_id: int) -> None:
    cart_item = get_cart_item(db, user_id=user_id, product_id=product_id)
    if cart_item is None:
        return

    db.delete(cart_item)
    db.commit()
