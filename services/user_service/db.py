from sqlmodel import SQLModel, Session, create_engine


def get_engine(sqlite_path: str = "sqlite:///./users.db"):
    return create_engine(sqlite_path, connect_args={"check_same_thread": False})


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)


def get_session(engine):
    def _get_session():
        with Session(engine) as session:
            yield session

    return _get_session
