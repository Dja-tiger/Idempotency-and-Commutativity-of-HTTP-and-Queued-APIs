import os
from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from .clients import BillingClient, NotificationClient, UserClient
from .db import get_engine, get_session, init_db
from .models import Order, OrderCreate, OrderRead, OrderStatus


def create_app() -> FastAPI:
    app = FastAPI(title="Order Service")
    engine = get_engine(os.getenv("ORDER_DB", "sqlite:///./orders.db"))
    init_db(engine)
    session_provider = get_session(engine)

    billing_client = BillingClient()
    notification_client = NotificationClient()
    user_client = UserClient()

    @app.on_event("shutdown")
    async def shutdown_event():
        await billing_client.close()
        await notification_client.close()
        await user_client.close()

    @app.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
    async def create_order(
        payload: OrderCreate,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
        session=Depends(session_provider),
    ):
        if idempotency_key:
            existing_order = session.exec(
                select(Order).where(Order.idempotency_key == idempotency_key)
            ).first()
            if existing_order:
                return OrderRead(**existing_order.model_dump())

        try:
            user = await user_client.get_user(payload.user_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        withdrawal_success = False
        message = ""
        payment: dict[str, float | str] = {}
        try:
            payment = await billing_client.withdraw(payload.user_id, payload.price)
            withdrawal_success = payment.get("withdrawn", False)
            message = payment.get("message", "")
        except Exception:
            withdrawal_success = False
            message = "Billing unavailable"

        status_value = OrderStatus.CONFIRMED if withdrawal_success else OrderStatus.FAILED
        email_body = (
            f"Письмо счастья: заказ на сумму {payload.price} подтвержден. Баланс {payment.get('balance', 'n/a')}"
            if withdrawal_success
            else f"Письмо горя: не удалось списать {payload.price}. {message}"
        )

        order = Order(
            user_id=payload.user_id,
            price=payload.price,
            status=status_value,
            message=email_body,
            idempotency_key=idempotency_key,
        )
        session.add(order)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            existing_order = session.exec(
                select(Order).where(Order.idempotency_key == idempotency_key)
            ).first()
            if existing_order:
                return OrderRead(**existing_order.model_dump())
            raise

        session.refresh(order)

        await notification_client.send_email(
            user_id=payload.user_id,
            email=user["email"],
            subject="Результат оформления заказа",
            body=email_body,
        )

        return OrderRead(**order.model_dump())

    @app.get("/orders", response_model=list[OrderRead])
    async def list_orders(user_id: int | None = None, session=Depends(session_provider)):
        statement = select(Order)
        if user_id is not None:
            statement = statement.where(Order.user_id == user_id)
        orders = session.exec(statement.order_by(Order.created_at)).all()
        return [OrderRead(**item.model_dump()) for item in orders]

    return app


app = create_app()
