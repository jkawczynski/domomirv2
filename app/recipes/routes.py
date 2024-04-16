from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from templates import templates

from common import htmx_utils
from recipes import forms, services
from recipes.crud import RecipeCrud, RecipeImageCrud
from shopping.tasks import add_ingredients_to_shopping_list

router = APIRouter()


async def get_recipes_context(
    crud: RecipeCrud = Depends(RecipeCrud),
) -> dict:
    recipes = await crud.get_list()
    return {"recipes": list(recipes)}


@router.post("/upload")
async def upload_file(
    request: Request,
    files: list[UploadFile],
    crud: RecipeImageCrud = Depends(RecipeImageCrud),
    service: services.RecipeImageService = Depends(services.RecipeImageService),
):
    form = await request.form()
    existing_images = await crud.get_list_by_ids(
        images_ids=[int(image_id) for image_id in form.getlist("images")]
    )
    db_images = await service.upload_and_save_images(files)
    context = {
        "errors": {},
        "recipe": {
            "ingredients": [{} for i in range(3)],
            "images": existing_images + db_images,
        },
    }
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="recipes/_partials/form_recipe_images.html",
        full_template="recipes/create.html",
    )


@router.get("", response_class=HTMLResponse)
async def index(
    request: Request,
    recipes_context: Annotated[dict, Depends(get_recipes_context)],
):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=recipes_context,
        partial_template="recipes/_partials/index.html",
        full_template="recipes/index.html",
    )


@router.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    query: str | None = None,
    crud: RecipeCrud = Depends(RecipeCrud),
):
    recipes = await crud.get_list(query)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"recipes": list(recipes)},
        partial_template="recipes/_partials/recipes_list.html",
        full_template="recipes/index.html",
    )


@router.get("/form", response_class=HTMLResponse)
async def get_form(request: Request):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"errors": {}, "recipe": {"ingredients": [{} for i in range(3)]}},
        partial_template="recipes/_partials/form.html",
        full_template="recipes/index.html",
    )


@router.patch("/more-ingredients", response_class=HTMLResponse)
async def more_ingredients(
    request: Request,
    form_data: Annotated[dict, Body()],
):
    form = forms.RecipeCreateForm(form_data)
    form.clean()
    form.add_empty_ingredients()
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"errors": {}, "recipe": form_data},
        partial_template="recipes/_partials/form_ingredients.html",
        full_template="recipes/create.html",
    )


@router.get("/create", response_class=HTMLResponse)
async def create(request: Request):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"errors": {}, "recipe": {"ingredients": [{} for i in range(3)]}},
        partial_template="recipes/_partials/create.html",
        full_template="recipes/create.html",
    )


@router.post("", response_class=HTMLResponse)
async def create_recipe(
    request: Request,
    form_data: Annotated[dict, Body()],
    service: services.RecipeService = Depends(services.RecipeService),
    crud: RecipeCrud = Depends(RecipeCrud),
):
    context = {"recipe": form_data, "errors": {}}
    form = forms.RecipeCreateForm(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        form.add_empty_ingredients()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="recipes/_partials/create.html",
            full_template="recipes/create.html",
        )

    recipe = await service.create_recipe(
        form.validated_model,
        form.images_ids,
    )

    context = {"action": "created", "recipe": recipe, **await get_recipes_context(crud)}
    headers = {"HX-Push-Url": "/recipes"}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        headers=headers,
        partial_template="recipes/_partials/index.html",
        full_template="recipes/index.html",
    )


@router.post("/add-to-shopping-list", response_class=HTMLResponse)
async def create_from_ingredients(
    request: Request,
    form_data: Annotated[dict, Body()],
):
    form = forms.IngredientsIdsForm(form_data)
    if not form.is_valid():
        raise HTTPException(status_code=400, detail="No ingredients provided")

    ingredients_ids = form.validated_model.ingredients
    await add_ingredients_to_shopping_list.kiq(ingredients_ids)


@router.get("/{recipe_id}", response_class=HTMLResponse)
async def recipe_details(
    request: Request,
    recipe_id: int,
    crud: RecipeCrud = Depends(RecipeCrud),
):
    recipe = await crud.get_by_id(recipe_id)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"recipe": recipe},
        partial_template="recipes/_partials/details.html",
        full_template="recipes/details.html",
    )


@router.get("/{recipe_id}/edit", response_class=HTMLResponse)
async def get_recipe_edit(
    request: Request,
    recipe_id: int,
    crud: RecipeCrud = Depends(RecipeCrud),
):
    recipe = await crud.get_by_id(recipe_id)
    context = {"recipe": recipe, "errors": {}}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="recipes/_partials/edit.html",
        full_template="recipes/edit.html",
    )


@router.put("/{recipe_id}", response_class=HTMLResponse)
async def edit_recipe(
    request: Request,
    recipe_id: int,
    form_data: Annotated[dict, Body()],
    crud: RecipeCrud = Depends(RecipeCrud),
    service: services.RecipeService = Depends(services.RecipeService),
):
    context = {"recipe": form_data, "errors": {}}
    recipe = await crud.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    form = forms.RecipeCreateForm(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        form.add_empty_ingredients()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="recipes/_partials/edit.html",
            full_template="recipes/edit.html",
        )

    recipe = await service.edit_recipe(
        db_recipe=recipe,
        validated_recipe=form.validated_model,
        images_ids=form.images_ids,
    )

    context = {"action": "edited", "recipe": recipe, **await get_recipes_context(crud)}
    headers = {"HX-Push-Url": "/recipes"}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        headers=headers,
        partial_template="recipes/_partials/index.html",
        full_template="recipes/index.html",
    )


@router.delete("/{recipe_id}", response_class=HTMLResponse)
async def delete_recipe(
    request: Request,
    recipe_id: int,
    crud: RecipeCrud = Depends(RecipeCrud),
):
    recipe = await crud.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    await crud.delete(recipe)

    context = {"action": "deleted", **await get_recipes_context(crud)}
    headers = {"HX-Push-Url": "/recipes"}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        headers=headers,
        partial_template="recipes/_partials/index.html",
        full_template="recipes/index.html",
    )
