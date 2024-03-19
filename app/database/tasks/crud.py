from collections.abc import Iterable, Sequence

from database.tasks.models import Task
from sqlalchemy import delete, func
from sqlmodel import Session, col, select


def get_list(db: Session) -> Sequence[Task]:
    stmt = select(Task).order_by(col(Task.completed).desc(), col(Task.id))
    return db.exec(stmt).all()


def get_unfinished(db: Session) -> Sequence[Task]:
    stmt = select(Task).where(col(Task.completed).is_(None))
    return db.exec(stmt).all()


def get_unfinished_count(db: Session) -> int:
    stmt = select(func.count(col(Task.id))).where(col(Task.completed).is_(None))
    return db.scalar(stmt) or 0


def get_by_id(db: Session, task_id: int) -> Task | None:
    stmt = select(Task).where(Task.id == task_id)
    return db.exec(stmt).first()


def persist(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def persist_all(db: Session, tasks: Iterable[Task]):
    for task in tasks:
        db.add(task)

    db.commit()


def remove_all_finished(db: Session):
    stmt = delete(Task).where(col(Task.completed).is_not(None))
    db.exec(stmt)
    db.commit()
