from collections.abc import Sequence

from sqlmodel import Session, col, select

from . import models


def get_list(db: Session) -> Sequence[models.User]:
    stmt = select(models.User).order_by(col(models.User.id).desc())
    return db.exec(stmt).all()


def get_by_id(db: Session, user_id: int) -> models.User | None:
    stmt = select(models.User).where(models.User.id == user_id)
    return db.exec(stmt).first()


def get_by_name(db: Session, name: str) -> models.User | None:
    stmt = select(models.User).where(models.User.name == name)
    return db.exec(stmt).first()


def persist(db: Session, user: models.User) -> models.User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
