from datetime import date, datetime, timedelta

from database.schedules import crud as schedule_crud
from database.tasks import crud, models
from database.users import crud as users_crud
from fastapi import HTTPException
from integrations.mqtt.tasks import send_mqtt_task_assigned
from sqlmodel import Session


def create_task(db: Session, task: models.TaskCreate) -> None:
    db_task = models.Task.model_validate(task)
    crud.persist(db, db_task)


def assign_task(db: Session, task_id: int, user_id: int) -> None:
    task = crud.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user = users_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task.assigned_to = user
    crud.persist(db, task)
    send_mqtt_task_assigned.delay(task.id)


def undo_complete_task(db: Session, task_id: int) -> None:
    task = crud.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = None
    crud.persist(db, task)


def complete_task(db: Session, task_id: int) -> None:
    task = crud.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.completed:
        return

    task.completed = datetime.now()
    crud.persist(db, task)

    if task.schedule_id and (schedule := schedule_crud.get_by_id(db, task.schedule_id)):
        frequency_in_days = schedule.frequency_in_days
        if not frequency_in_days:
            schedule_crud.remove(db, schedule)
            return

        target_date = schedule.schedule_date
        while target_date <= date.today():
            target_date = target_date + timedelta(days=frequency_in_days)

        schedule.schedule_date = target_date
        schedule_crud.persist(db, schedule)
