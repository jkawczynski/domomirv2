from typing import Annotated

from common import htmx_utils
from database import get_session
from database.schedules import crud
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from forms import schedules as schedules_forms
from services import schedules as schedules_service
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def get_schedules_context(session: AsyncSession) -> dict:
    return {"schedules": await crud.get_list(session)}


@router.get("/", response_class=HTMLResponse)
async def get_schedules(request: Request, session: AsyncSession = Depends(get_session)):
    context = await get_schedules_context(session)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="schedules/_partials/index.html",
        full_template="schedules/index.html",
    )


@router.get("/create", response_class=HTMLResponse)
async def get_create_schedule_form(request: Request):
    context = {"errors": {}, "schedule": {}}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="schedules/_partials/create.html",
        full_template="schedules/create.html",
    )


@router.get("/{schedule_id}", response_class=HTMLResponse)
async def get_schedule(
    request: Request,
    schedule_id: int,
    session: AsyncSession = Depends(get_session),
):
    context = {
        "errors": {},
        "schedule": await crud.get_by_id(session, schedule_id),
        "schedule_id": schedule_id,
    }
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="schedules/_partials/edit.html",
        full_template="schedules/edit.html",
    )


@router.post("/create", response_class=HTMLResponse)
async def create_schedule(
    request: Request,
    form_data: Annotated[dict, Body()],
    session: AsyncSession = Depends(get_session),
):
    context = {"schedule": form_data, "errors": {}}
    form = schedules_forms.ScheduleForm(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="schedules/_partials/create.html",
            full_template="schedules/create.html",
        )

    schedule = await schedules_service.create_schedule(session, form.validated_model)

    context = {
        "schedule": schedule,
        "action": "created",
        **await get_schedules_context(session),
    }
    headers = {"HX-Push-Url": "/schedules"}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        partial_template="schedules/_partials/index.html",
        full_template="schedules/index.html",
        headers=headers,
        context=context,
    )


@router.put("/{schedule_id}", response_class=HTMLResponse)
async def edit_schedule(
    request: Request,
    schedule_id: int,
    form_data: Annotated[dict, Body()],
    session: AsyncSession = Depends(get_session),
):
    context = {"schedule_id": schedule_id, "schedule": form_data, "errors": {}}
    form = schedules_forms.ScheduleForm(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="schedules/_partials/edit.html",
            full_template="schedules/edit.html",
        )

    schedule = await schedules_service.edit_schedule(
        session=session,
        input_schedule=form.validated_model,
        schedule_id=schedule_id,
    )

    context = {
        "schedule": schedule,
        "action": "edited",
        **await get_schedules_context(session),
    }
    headers = {"HX-Push-Url": "/schedules"}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        partial_template="schedules/_partials/index.html",
        full_template="schedules/index.html",
        headers=headers,
        context=context,
    )
