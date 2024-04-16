from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import HTMLResponse
from templates import templates

from common import htmx_utils
from schedules import forms
from schedules.crud import ScheduleCrud
from schedules.services import ScheduleService

router = APIRouter()


async def get_schedules_context(crud: ScheduleCrud = Depends(ScheduleCrud)) -> dict:
    return {"schedules": await crud.get_list()}


@router.get("", response_class=HTMLResponse)
async def index(
    request: Request,
    schedules_context: Annotated[dict, Depends(get_schedules_context)],
):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=schedules_context,
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
    crud: ScheduleCrud = Depends(ScheduleCrud),
):
    context = {
        "errors": {},
        "schedule": await crud.get_by_id(schedule_id),
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
    crud: ScheduleCrud = Depends(ScheduleCrud),
    service: ScheduleService = Depends(ScheduleService),
):
    context = {"schedule": form_data, "errors": {}}
    form = forms.ScheduleForm(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="schedules/_partials/create.html",
            full_template="schedules/create.html",
        )

    schedule = await service.create_schedule(form.validated_model)

    context = {
        "schedule": schedule,
        "action": "created",
        **await get_schedules_context(crud),
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
    crud: ScheduleCrud = Depends(ScheduleCrud),
    service: ScheduleService = Depends(ScheduleService),
):
    context = {"schedule_id": schedule_id, "schedule": form_data, "errors": {}}
    form = forms.ScheduleForm(form_data)
    if not form.is_valid():
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="schedules/_partials/edit.html",
            full_template="schedules/edit.html",
        )

    schedule = await service.edit_schedule(
        input_schedule=form.validated_model,
        schedule_id=schedule_id,
    )

    context = {
        "schedule": schedule,
        "action": "edited",
        **await get_schedules_context(crud),
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
