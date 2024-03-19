from config import get_settings
from sqlmodel import Session, SQLModel, create_engine

from .schedules import models  # noqa E501
from .tasks import models  # noqa E501
from .users import models  # noqa E501

settings = get_settings()

SQLALCHEMY_DATABASE_URL = get_settings().database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def drop_all():
    SQLModel.metadata.drop_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
