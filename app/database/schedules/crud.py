from collections.abc import Sequence
from datetime import date

from database.schedules.models import Schedule
from database.tasks.models import Task
from sqlalchemy import delete
from sqlmodel import Session, col, select


def get_list(db: Session) -> Sequence[Schedule]:
    stmt = select(Schedule).order_by(col(Schedule.schedule_date))
    return db.exec(stmt).all()


def get_scheduled_for_day(
    db: Session, day: date, exclude_ids: list[int] | None = None
) -> Sequence[Schedule]:
    exclude_ids = exclude_ids or []
    stmt = (
        select(Schedule)
        .where(Schedule.schedule_date == day)
        .where(Schedule.id not in exclude_ids)
    )
    return db.exec(stmt).all()


def get_by_id(db: Session, schedule_id: int) -> Schedule | None:
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    return db.exec(stmt).first()


def persist(db: Session, schedule: Schedule) -> Schedule:
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def remove(db: Session, schedule: Schedule):
    db.delete(schedule)
    db.commit()


def remove_all_finished(db: Session):
    today = date.today()
    subquery = (
        select(Task.id)
        .where(col(Task.completed).is_not(None))
        .where(col(Task.schedule_id).is_not(None))
        .scalar_subquery()
    )

    stmt = (
        delete(Schedule)
        .where(col(Schedule.schedule_date) < today)
        .where(col(Schedule.id).not_in(subquery))
    )
    db.exec(stmt)
    db.commit()
