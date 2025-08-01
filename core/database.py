from sqlmodel import SQLModel, create_engine, Session

engine = create_engine("sqlite:///data.db")
SQLModel.metadata.create_all(engine)

# created in order to avoid manually opening and closing the databse session,
# and to be directly used as a dependency


def create_session():
    with Session(engine) as session:
        yield session

# the contxt manager is kept open until the function using the session
# is done completely
