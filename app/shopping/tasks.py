from database import get_session
from recipes import crud as recipes_crud
from shopping import crud as shopping_crud
from shopping import models as shopping_models
from tkq import DEFAULT_SCHEDULE_ARGS, broker


@broker.task(schedule=[{"cron": "0 2 * * *", **DEFAULT_SCHEDULE_ARGS}])
async def clear_completed_items():
    session_maker = get_session()
    session = await anext(session_maker)

    await shopping_crud.remove_all_completed(session)


@broker.task()
async def add_ingredients_to_shopping_list(ingredients_ids: list[int]):
    session_maker = get_session()
    session = await anext(session_maker)

    ingredients = await recipes_crud.get_ingredients_by_ids(session, ingredients_ids)

    items = []
    for ingredient in ingredients:
        name = ingredient.name
        if ingredient.amount_and_unit:
            name += f" - {ingredient.amount_and_unit}"
        items.append(shopping_models.ShoppingListItem(name=name))

    await shopping_crud.persist_all(session, items)
