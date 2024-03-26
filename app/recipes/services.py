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
    recipe: models.RecipeCreate,
    images_ids: list[int] | None = None,
):
    db_schedule = models.Recipe.model_validate(recipe)
    db_recipe = await crud.persist(session, db_schedule)
    if images_ids:
        await crud.connect_recipe_with_images(session, db_recipe, images_ids)

    return recipe
