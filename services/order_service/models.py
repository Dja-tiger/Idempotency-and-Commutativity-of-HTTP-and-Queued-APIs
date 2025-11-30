from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel


class Order(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: int
    price: float = SQLField(gt=0)
    status: str
    message: str
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class OrderCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    price: float = Field(..., gt=0)


class OrderRead(BaseModel):
    id: int
    user_id: int
    price: float
    status: str
    message: str
    created_at: datetime
