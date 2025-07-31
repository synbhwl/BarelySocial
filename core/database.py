from sqlmodel import SQLModel, create_engine, Session

engine = create_engine("sqlite:///data.db")
SQLModel.metadata.create_all(engine)


def create_session():
    with Session(engine) as session:
        yield session
