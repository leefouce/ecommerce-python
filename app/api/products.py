from fastapi import APIRouter, HTTPException

from app.data.products import get_product_by_id, list_products
from app.schemas.product import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[Product])
def get_products() -> list[Product]:
    return list_products()


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int) -> Product:
    product = get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
