from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import ProductModel
from app.repositories.products import (
    create_product,
    delete_product,
    get_product_by_id,
    update_product,
)
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.security.auth import get_current_admin_user

router = APIRouter(prefix="/admin/products", tags=["admin-products"])


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_admin_product(
    payload: ProductCreate,
    _: object = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> ProductModel:
    return create_product(
        db,
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )


@router.patch("/{product_id}", response_model=Product)
def update_admin_product(
    product_id: int,
    payload: ProductUpdate,
    _: object = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> ProductModel:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return update_product(
        db,
        product,
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_product(
    product_id: int,
    _: object = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    delete_product(db, product)
