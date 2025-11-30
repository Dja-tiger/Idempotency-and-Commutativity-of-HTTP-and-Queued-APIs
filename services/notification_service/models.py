from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel


class Notification(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: int
    email: EmailStr
    subject: str
    body: str
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class NotificationRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    email: EmailStr
    subject: str
    body: str


class NotificationRead(BaseModel):
    id: int
    user_id: int
    email: EmailStr
    subject: str
    body: str
    created_at: datetime


class NotificationList(BaseModel):
    items: list[NotificationRead]
