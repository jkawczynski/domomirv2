from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from templates import templates

from common import htmx_utils
from database import get_session
from shopping import crud, forms, services

router = APIRouter()


async def get_context(session: AsyncSession) -> dict:
    return {"items": await crud.get_list(session)}


@router.get("", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=await get_context(session),
        partial_template="shopping/_partials/index.html",
        full_template="shopping/index.html",
    )


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    form_data: Annotated[dict, Body()],
    session: AsyncSession = Depends(get_session),
):
    context = {"item": form_data}
    form = forms.ShoppingListItemFormCreate(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="shopping/_partials/add_item.html",
            full_template="shopping/index.html",
            status_code=400,
        )

    await services.create_shopping_list_item(session, form.validated_model)
    context = await get_context(session)
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
    session: AsyncSession = Depends(get_session),
):
    context = {"item": form_data}
    form = forms.ShoppingListItemFormEdit(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        raise HTTPException(status_code=500, detail="unhandled")

    await services.update_item(session, item_id, form.validated_model)
    context = await get_context(session)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="shopping/_partials/items.html",
        full_template="shopping/index.html",
    )
