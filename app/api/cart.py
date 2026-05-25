from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cart import CartItemModel
from app.models.user import UserModel
from app.repositories.cart import add_cart_item, list_cart_items, remove_cart_item
from app.repositories.products import get_product_by_id
from app.schemas.cart import CartItem, CartItemCreate
from app.security.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/items", response_model=list[CartItem])
def read_cart_items(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CartItemModel]:
    return list_cart_items(db, user_id=current_user.id)


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    product_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    remove_cart_item(db, user_id=current_user.id, product_id=product_id)


@router.post("/items", response_model=CartItem, status_code=status.HTTP_201_CREATED)
def create_cart_item(
    payload: CartItemCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartItemModel:
    product = get_product_by_id(db, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return add_cart_item(
        db,
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )
