import inspect
from functools import partial, wraps

import asyncer
from rich import print
from typer import Typer

from database import get_session
from shopping.crud import ShoppingListItemCrud
from users import models
from users.crud import UserCrud


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
    crud = UserCrud(session)
    user = await crud.get_by_name(name)
    if user:
        print_err(f"User with {name=} already exist!")
        return

    user = models.User(name=name)
    await crud.persist(user)

    print_success(f"Created user with {name=}")


@app.command()
async def clear_shopping():
    session_maker = get_session()
    session = await anext(session_maker)
    crud = ShoppingListItemCrud(session)
    await crud.delete_all_completed()


if __name__ == "__main__":
    app()
