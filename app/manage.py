import typer
from database import create_db_and_tables, engine
from database.users import crud as users_crud
from database.users import models as users_models
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


if __name__ == "__main__":
    app()
