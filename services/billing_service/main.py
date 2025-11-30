import os
from fastapi import Depends, FastAPI, HTTPException, status

from .db import get_engine, get_session, init_db
from .models import Account, AccountCreate, AccountRead, PaymentRequest, PaymentResult


def create_app() -> FastAPI:
    app = FastAPI(title="Billing Service")
    engine = get_engine(os.getenv("BILLING_DB", "sqlite:///./billing.db"))
    init_db(engine)
    session_provider = get_session(engine)

    @app.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
    def create_account(payload: AccountCreate, session=Depends(session_provider)):
        existing = session.get(Account, payload.user_id)
        if existing:
            return AccountRead(user_id=existing.user_id, balance=existing.balance)

        account = Account(user_id=payload.user_id, balance=0)
        session.add(account)
        session.commit()
        session.refresh(account)
        return AccountRead(user_id=account.user_id, balance=account.balance)

    @app.get("/accounts/{user_id}", response_model=AccountRead)
    def get_account(user_id: int, session=Depends(session_provider)):
        account = session.get(Account, user_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return AccountRead(user_id=account.user_id, balance=account.balance)

    @app.post("/accounts/{user_id}/deposit", response_model=AccountRead)
    def deposit(user_id: int, payload: PaymentRequest, session=Depends(session_provider)):
        account = session.get(Account, user_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        account.balance += payload.amount
        session.add(account)
        session.commit()
        session.refresh(account)
        return AccountRead(user_id=account.user_id, balance=account.balance)

    @app.post("/accounts/{user_id}/withdraw", response_model=PaymentResult)
    def withdraw(user_id: int, payload: PaymentRequest, session=Depends(session_provider)):
        account = session.get(Account, user_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        if account.balance < payload.amount:
            return PaymentResult(
                user_id=user_id,
                balance=account.balance,
                withdrawn=False,
                message="Insufficient funds",
            )

        account.balance -= payload.amount
        session.add(account)
        session.commit()
        session.refresh(account)
        return PaymentResult(
            user_id=user_id,
            balance=account.balance,
            withdrawn=True,
            message="Payment accepted",
        )

    return app


app = create_app()
