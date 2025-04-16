from pydantic import BaseModel


class MenuItemSchema(BaseModel):
    id: int
    name: str
    price: float
    available: bool

    class Config:
        orm_mode = True
