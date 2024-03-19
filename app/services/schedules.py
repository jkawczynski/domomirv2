from database.schedules import crud, models
from fastapi import HTTPException
from sqlmodel import Session


def create_schedule(db: Session, schedule: models.ScheduleCreate) -> models.Schedule:
    db_schedule = models.Schedule.model_validate(schedule)
    return crud.persist(db, db_schedule)


def edit_schedule(
    db: Session,
    input_schedule: models.ScheduleCreate,
    schedule_id: int,
) -> models.Schedule:
    schedule = crud.get_by_id(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.name = input_schedule.name
    schedule.schedule_date = input_schedule.schedule_date
    schedule.frequency_in_days = input_schedule.frequency_in_days
    schedule = crud.persist(db, schedule)
    return schedule
