from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import OrderModel
from app.models.user import UserModel
from app.repositories.orders import create_order_from_cart, list_orders
from app.schemas.order import Order
from app.security.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[Order])
def read_orders(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderModel]:
    return list_orders(db, user_id=current_user.id)


@router.post("/checkout", response_model=Order, status_code=status.HTTP_201_CREATED)
def checkout_cart(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderModel:
    return create_order_from_cart(db, user_id=current_user.id)
