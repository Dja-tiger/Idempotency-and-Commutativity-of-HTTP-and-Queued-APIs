from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel


class OrderStatus(str, Enum):
    CONFIRMED = "confirmed"
    FAILED = "failed"


class Order(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(index=True)
    price: float = SQLField(gt=0)
    status: OrderStatus = SQLField(index=True)
    message: str
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    idempotency_key: Optional[str] = SQLField(default=None, index=True, unique=True)


class OrderCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    price: float = Field(..., gt=0)


class OrderRead(BaseModel):
    id: int
    user_id: int
    price: float
    status: OrderStatus
    message: str
    created_at: datetime
