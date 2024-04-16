from config import get_settings
from fastapi import Depends
from fastapi.datastructures import UploadFile

from recipes import models, upload
from recipes.crud import RecipeCrud, RecipeImageCrud, RecipeIngredientCrud

settings = get_settings()


class RecipeService:
    def __init__(
        self,
        crud: RecipeCrud = Depends(RecipeCrud),
        ingredient_crud: RecipeIngredientCrud = Depends(RecipeIngredientCrud),
    ) -> None:
        self.crud = crud
        self.ingredient_crud = ingredient_crud

    async def create_recipe(
        self,
        recipe_form: models.RecipeCreate,
        images_ids: list[int] | None = None,
    ):
        db_recipe = await self.crud.persist(models.Recipe.model_validate(recipe_form))
        if images_ids:
            await self.crud.connect_recipe_with_images(db_recipe, images_ids)

        return db_recipe

    async def edit_recipe(
        self,
        db_recipe: models.Recipe,
        validated_recipe: models.RecipeCreate,
        images_ids: list[int] | None = None,
    ):
        db_recipe.name = validated_recipe.name
        db_recipe.description = validated_recipe.description
        db_recipe.url = validated_recipe.url

        await self.crud.persist(db_recipe)

        if images_ids:
            images_to_clear = [
                image.id for image in db_recipe.images if image.id not in images_ids
            ]
            await self.crud.remove_images(images_ids=images_to_clear)
            await self.crud.connect_recipe_with_images(db_recipe, images_ids)

        await self.update_recipe_ingredients(db_recipe, validated_recipe)
        return db_recipe

    async def update_recipe_ingredients(
        self,
        db_recipe: models.Recipe,
        validated_recipe: models.RecipeCreate,
    ):
        await self.crud.remove_ingredients(db_recipe)
        for ingredient in validated_recipe.ingredients:
            ingredient.recipe_id = db_recipe.id

        await self.ingredient_crud.persist_all(validated_recipe.ingredients)

    async def update_recipe_images(
        self,
        db_recipe: models.Recipe,
        images_ids: list[int],
    ):
        images_to_clear = [
            image.id for image in db_recipe.images if image.id not in images_ids
        ]
        await self.crud.remove_images(images_ids=images_to_clear)
        await self.crud.connect_recipe_with_images(db_recipe, images_ids)


def get_recipe_image_url(recipe_image: models.RecipeImage):
    file_name = recipe_image.file_name
    if settings.serve_local_images:
        base_path = settings.local_images_directory_path
    else:
        base_path = "TODO"

    return f"{base_path}/{file_name}"


class RecipeImageService:
    def __init__(self, crud: RecipeImageCrud = Depends(RecipeImageCrud)) -> None:
        self.crud = crud

    async def upload_and_save_images(
        self,
        files: list[UploadFile],
    ) -> list[models.RecipeImage]:
        images = []
        for file in files:
            file_name = upload.upload_image(file)
            db_image = models.RecipeImage(file_name=file_name)
            db_image = await self.crud.persist(db_image)
            images.append(db_image)
        return images
