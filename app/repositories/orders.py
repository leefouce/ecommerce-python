from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import OrderItemModel, OrderModel
from app.repositories.cart import list_cart_items


def list_orders(db: Session, *, user_id: int) -> list[OrderModel]:
    statement = (
        select(OrderModel)
        .where(OrderModel.user_id == user_id)
        .order_by(OrderModel.id)
    )
    return list(db.scalars(statement).all())


def create_order_from_cart(db: Session, *, user_id: int) -> OrderModel:
    cart_items = list_cart_items(db, user_id=user_id)
    order = OrderModel(user_id=user_id, status="created")
    order.items = [
        OrderItemModel(product_id=item.product_id, quantity=item.quantity)
        for item in cart_items
    ]

    db.add(order)
    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)
    return order
