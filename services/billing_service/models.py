# services/billing_service/models.py

from sqlmodel import SQLModel, Field
from pydantic import BaseModel, Field as PydanticField


class Account(SQLModel, table=True):
    """
    Табличная модель аккаунта в биллинге.
    user_id — PK, один аккаунт на одного пользователя.
    """
    user_id: int = Field(primary_key=True)
    balance: float = Field(default=0, ge=0)


class AccountCreate(BaseModel):
    """
    DTO для создания аккаунта (используется user-service).
    """
    user_id: int = PydanticField(..., ge=1)


class AccountRead(BaseModel):
    """
    DTO для отдачи информации об аккаунте наружу.
    """
    user_id: int
    balance: float


class PaymentRequest(BaseModel):
    """
    Запрос на операцию с балансом (депозит или списание).
    """
    amount: float = PydanticField(..., gt=0)


class PaymentResult(BaseModel):
    """
    Результат операции со счётом.
    """
    user_id: int
    balance: float
    withdrawn: bool
    message: str
