from pydantic import BaseModel, ConfigDict


class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int


class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    items: list[OrderItem]
