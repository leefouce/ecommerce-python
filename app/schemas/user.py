from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
