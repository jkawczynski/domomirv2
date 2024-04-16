from database import get_session
from recipes.crud import RecipeIngredientCrud
from shopping import models as shopping_models
from shopping.crud import ShoppingListItemCrud
from tkq import DEFAULT_SCHEDULE_ARGS, broker


@broker.task(schedule=[{"cron": "0 2 * * *", **DEFAULT_SCHEDULE_ARGS}])
async def clear_completed_items():
    session_maker = get_session()
    session = await anext(session_maker)
    crud = ShoppingListItemCrud(session)

    await crud.delete_all_completed()


@broker.task()
async def add_ingredients_to_shopping_list(ingredients_ids: list[int]):
    session_maker = get_session()
    session = await anext(session_maker)
    ingredient_crud = RecipeIngredientCrud(session)
    shopping_crud = ShoppingListItemCrud(session)

    ingredients = await ingredient_crud.get_list_by_ids(ingredients_ids)

    items = []
    for ingredient in ingredients:
        name = ingredient.name
        if ingredient.amount_and_unit:
            name += f" - {ingredient.amount_and_unit}"
        items.append(shopping_models.ShoppingListItem(name=name))

    await shopping_crud.persist_all(items)
