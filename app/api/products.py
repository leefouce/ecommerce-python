from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import ProductModel
from app.repositories.products import get_product_by_id, list_products
from app.schemas.product import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[Product])
def get_products(db: Session = Depends(get_db)) -> list[ProductModel]:
    return list_products(db)


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductModel:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
