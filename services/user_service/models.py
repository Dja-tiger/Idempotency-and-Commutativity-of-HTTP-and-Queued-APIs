from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    email: EmailStr
    name: str


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
