from pydantic import BaseModel


class TableSchema(BaseModel):
    id: int
    status: str

    class Config:
        orm_mode = True
