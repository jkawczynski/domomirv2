from config import get_settings
from fastapi.datastructures import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from recipes import crud, models, upload

settings = get_settings()


def get_recipe_image_url(recipe_image: models.RecipeImage):
    file_name = recipe_image.file_name
    if settings.serve_local_images:
        base_path = settings.local_images_directory_path
    else:
        base_path = "TODO"

    return f"{base_path}/{file_name}"


async def upload_and_save_images(
    session: AsyncSession, files: list[UploadFile]
) -> list[models.RecipeImage]:
    images = []
    for file in files:
        file_name = upload.upload_image(file)
        db_image = models.RecipeImage(file_name=file_name)
        db_image = await crud.persist(session, db_image)
        images.append(db_image)
    return images


async def create_recipe(
    session: AsyncSession,
    recipe_form: models.RecipeCreate,
    images_ids: list[int] | None = None,
):
    db_recipe = await crud.persist(session, models.Recipe.model_validate(recipe_form))
    if images_ids:
        await crud.connect_recipe_with_images(session, db_recipe, images_ids)

    return db_recipe


async def update_recipe_images(
    session: AsyncSession,
    db_recipe: models.Recipe,
    images_ids: list[int],
):
    images_to_clear = [
        image.id for image in db_recipe.images if image.id not in images_ids
    ]
    await crud.remove_recipe_images(session, images_ids=images_to_clear)
    await crud.connect_recipe_with_images(session, db_recipe, images_ids)


async def update_recipe_ingredients(
    session: AsyncSession,
    db_recipe: models.Recipe,
    validated_recipe: models.RecipeCreate,
):
    await crud.remove_recipe_ingredients(session, db_recipe)
    for ingredient in validated_recipe.ingredients:
        ingredient.recipe_id = db_recipe.id

    await crud.persist_all(session, validated_recipe.ingredients)


async def edit_recipe(
    session: AsyncSession,
    db_recipe: models.Recipe,
    validated_recipe: models.RecipeCreate,
    images_ids: list[int] | None = None,
):
    db_recipe.name = validated_recipe.name
    db_recipe.description = validated_recipe.description
    db_recipe.url = validated_recipe.url

    await crud.persist(session, db_recipe)

    if images_ids:
        images_to_clear = [
            image.id for image in db_recipe.images if image.id not in images_ids
        ]
        await crud.remove_recipe_images(session, images_ids=images_to_clear)
        await crud.connect_recipe_with_images(session, db_recipe, images_ids)

    await update_recipe_ingredients(session, db_recipe, validated_recipe)
    return db_recipe
