import inspect
from functools import partial, wraps

import asyncer
from database import get_session
from database.users import crud as users_crud
from database.users import models as users_models
from rich import print
from typer import Typer


class AsyncTyper(Typer):
    @staticmethod
    def maybe_run_async(decorator, f):
        if inspect.iscoroutinefunction(f):

            @wraps(f)
            def runner(*args, **kwargs):
                return asyncer.runnify(f)(*args, **kwargs)

            decorator(runner)
        else:
            decorator(f)
        return f

    def callback(self, *args, **kwargs):
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)


app = AsyncTyper()


def print_err(msg: str):
    print(f"[bold red]{msg}[/bold red]")


def print_success(msg: str):
    print(f"[green]{msg}[/green]")


@app.command()
async def create_user(name: str):
    session_maker = get_session()
    session = await anext(session_maker)
    user = await users_crud.get_by_name(session, name)
    if user:
        print_err(f"User with {name=} already exist!")
        return

    user = users_models.User(name=name)
    await users_crud.persist(session, user)

    print_success(f"Created user with {name=}")


if __name__ == "__main__":
    app()
