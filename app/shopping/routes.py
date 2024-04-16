from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from templates import templates

from common import htmx_utils
from shopping import forms
from shopping.crud import ShoppingListItemCrud
from shopping.services import ShoppingListItemService

router = APIRouter()


async def get_context(
    crud: ShoppingListItemCrud = Depends(ShoppingListItemCrud),
) -> dict:
    return {"items": await crud.get_list()}


@router.get("", response_class=HTMLResponse)
async def index(request: Request, context: Annotated[dict, Depends(get_context)]):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="shopping/_partials/index.html",
        full_template="shopping/index.html",
    )


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    form_data: Annotated[dict, Body()],
    crud: ShoppingListItemCrud = Depends(ShoppingListItemCrud),
    service: ShoppingListItemService = Depends(ShoppingListItemService),
):
    context = {"item": form_data}
    form = forms.ShoppingListItemFormCreate(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        base_context = await get_context(crud)
        context.update(base_context)
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="shopping/_partials/add_item.html",
            full_template="shopping/index.html",
            status_code=400,
        )

    await service.create_shopping_list_item(form.validated_model)
    context = await get_context(crud)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="shopping/_partials/items.html",
        full_template="shopping/index.html",
    )


@router.patch("/{item_id}", response_class=HTMLResponse)
async def update(
    request: Request,
    item_id: int,
    form_data: Annotated[dict, Body()],
    crud: ShoppingListItemCrud = Depends(ShoppingListItemCrud),
    service: ShoppingListItemService = Depends(ShoppingListItemService),
):
    context = {"item": form_data}
    form = forms.ShoppingListItemFormEdit(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        raise HTTPException(status_code=500, detail="unhandled")

    await service.update_item(item_id, form.validated_model)
    context = await get_context(crud)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="shopping/_partials/items.html",
        full_template="shopping/index.html",
    )
