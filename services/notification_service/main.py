import os
from fastapi import Depends, FastAPI, status
from sqlmodel import select

from .db import get_engine, get_session, init_db
from .models import Notification, NotificationList, NotificationRead, NotificationRequest


def create_app() -> FastAPI:
    app = FastAPI(title="Notification Service")
    engine = get_engine(os.getenv("NOTIFICATION_DB", "sqlite:///./notifications.db"))
    init_db(engine)
    session_provider = get_session(engine)

    @app.post("/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
    def send_notification(payload: NotificationRequest, session=Depends(session_provider)):
        notification = Notification(**payload.model_dump())
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return NotificationRead(**notification.model_dump())

    @app.get("/notifications", response_model=NotificationList)
    def list_notifications(user_id: int | None = None, session=Depends(session_provider)):
        statement = select(Notification)
        if user_id is not None:
            statement = statement.where(Notification.user_id == user_id)
        notifications = session.exec(statement.order_by(Notification.created_at)).all()
        items = [NotificationRead(**item.model_dump()) for item in notifications]
        return NotificationList(items=items)

    return app


app = create_app()
