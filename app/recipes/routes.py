from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession

from common import htmx_utils
from database import get_session
from recipes import crud, filters, forms, services
from shopping.tasks import add_ingredients_to_shopping_list

router = APIRouter()
templates = Jinja2Templates(directory="templates")
templates.env.filters.update(filters.template_filters)


@router.post("/upload")
async def upload_file(
    request: Request,
    files: list[UploadFile],
    session: AsyncSession = Depends(get_session),
):
    db_images = await services.upload_and_save_images(session, files)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"images": db_images},
        partial_template="recipes/_partials/form_recipe_images.html",
        full_template="recipes/create.html",
    )


@router.get("", response_class=HTMLResponse)
async def index(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    recipes = await crud.get_list(session)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"recipes": list(recipes)},
        partial_template="recipes/_partials/index.html",
        full_template="recipes/index.html",
    )


@router.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    query: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    recipes = await crud.get_list(session, query)
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
    session: AsyncSession = Depends(get_session),
):
    context = {"recipe": form_data, "errors": {}}
    form = forms.RecipeCreateForm(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="recipes/_partials/create.html",
            full_template="recipes/create.html",
        )

    rec = form.validated_model
    await services.create_recipe(session, rec, form.images_ids)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="recipes/_partials/create.html",
        full_template="recipes/create.html",
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
    session: AsyncSession = Depends(get_session),
):
    recipe = await crud.get_by_id(session, recipe_id)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"recipe": recipe},
        partial_template="recipes/_partials/details.html",
        full_template="recipes/details.html",
    )
