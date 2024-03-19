import json
import os

import typer
from database import create_db_and_tables, drop_all, engine
from database.schedules import crud as schedules_crud
from database.schedules import models as schedules_models
from database.tasks import crud as tasks_crud
from database.tasks import models as tasks_models
from database.users import crud as users_crud
from database.users import models as users_models
from dateutil import parser
from integrations.mqtt.tasks import send_mqtt_remaining_tasks
from rich import print
from sqlmodel import Session
from tasks.tasks import clean_finished_tasks_and_schedules as clean_finished
from tasks.tasks import create_tasks_for_today as create_tasks

app = typer.Typer()


def print_err(msg: str):
    print(f"[bold red]{msg}[/bold red]")


def print_success(msg: str):
    print(f"[green]{msg}[/green]")


@app.command()
def create_user(name: str):
    with Session(engine) as session:
        user = users_crud.get_by_name(session, name)
        if user:
            print_err(f"User with {name=} already exist!")
            return

        user = users_models.User(name=name)
        users_crud.persist(session, user)

    print_success(f"Created user with {name=}")


@app.command()
def create_db():
    create_db_and_tables()


@app.command()
def create_tasks_for_today():
    clean_finished()
    create_tasks()


@app.command()
def send_remaining_tasks_mqtt():
    send_mqtt_remaining_tasks()


@app.command()
def import_data(path: str):
    if not os.path.exists(path):
        print_err("File doesn't exist")
        return

    drop_all()
    create_db_and_tables()

    input = {
        "users": [],
        "tasks": [],
        "schedules": [],
    }

    def get_frequency_in_days(schedule: dict) -> int:
        if schedule["repeat_every_x_days"]:
            return schedule["repeat_every_x_days"]

        if schedule["repeat_every_x_weeks"]:
            return schedule["repeat_every_x_weeks"] * 7

        if schedule["repeat_every_x_months"]:
            return schedule["repeat_every_x_months"] * 7 * 4

    with open(path) as f:
        data = json.loads(f.read())

    for row in data:
        if row["model"] == "todos.person":
            user = {"in_pk": row["pk"], "name": row["fields"]["name"]}
            input["users"].append(user)
        elif row["model"] == "todos.todotaskschedule":
            schedule = {
                "in_pk": row["pk"],
                "name": row["fields"]["name"],
                "schedule_date": row["fields"]["day_planned_to_complete"],
                "frequency_in_days": get_frequency_in_days(row["fields"]),
            }
            input["schedules"].append(schedule)
        elif row["model"] == "todos.todotask":
            task = {
                "in_pk": row["pk"],
                "name": row["fields"]["name"],
                "task_date": row["fields"]["day_planned_to_complete"],
                "schedule_pk": row["fields"]["schedule"],
                "completed": row["fields"]["completed"],
            }
            input["tasks"].append(task)

    schedule_id_map = {}
    with Session(engine) as session:
        for user_data in input["users"]:
            user = users_models.User(name=user_data["name"])
            users_crud.persist(session, user)

        for schedule_data in input["schedules"]:
            schedule = schedules_models.Schedule(
                name=schedule_data["name"],
                schedule_date=parser.parse(schedule_data["schedule_date"]),
                frequency_in_days=schedule_data["frequency_in_days"],
            )
            db_schedule = schedules_crud.persist(session, schedule)
            schedule_id_map[schedule_data["in_pk"]] = db_schedule.id

        for task_data in input["tasks"]:
            task = tasks_models.Task(
                name=task_data["name"],
                task_date=parser.parse(task_data["task_date"]),
                schedule_id=schedule_id_map[task_data["schedule_pk"]],
            )
            tasks_crud.persist(session, task)


if __name__ == "__main__":
    app()
