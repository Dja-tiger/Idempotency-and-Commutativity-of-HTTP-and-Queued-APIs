import os
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import select

from .clients import BillingClient
from .db import get_engine, get_session, init_db
from .models import User, UserCreate, UserRead


def create_app() -> FastAPI:
    app = FastAPI(title="User Service")
    engine = get_engine(os.getenv("USER_DB", "sqlite:///./users.db"))
    init_db(engine)
    session_provider = get_session(engine)
    billing_client = BillingClient()

    @app.on_event("shutdown")
    async def shutdown_event():
        await billing_client.close()

    @app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
    async def create_user(payload: UserCreate, session=Depends(session_provider)):
        existing = session.exec(select(User).where(User.email == payload.email)).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = User(email=payload.email, name=payload.name)
        session.add(user)
        session.commit()
        session.refresh(user)

        try:
            await billing_client.create_account(user.id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to create billing account")

        return UserRead(**user.model_dump())

    @app.get("/users/{user_id}", response_model=UserRead)
    async def get_user(user_id: int, session=Depends(session_provider)):
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserRead(**user.model_dump())

    @app.get("/users", response_model=list[UserRead])
    async def list_users(session=Depends(session_provider)):
        users = session.exec(select(User)).all()
        return [UserRead(**item.model_dump()) for item in users]

    return app


app = create_app()
