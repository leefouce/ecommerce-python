from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.cart import router as cart_router
from app.api.health import router as health_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.db.init_db import init_db

init_db()

app = FastAPI(
    title="Ecommerce API",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(products_router)
app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(orders_router)
