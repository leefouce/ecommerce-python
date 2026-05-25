from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
