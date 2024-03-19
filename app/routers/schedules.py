from typing import Annotated

from common import htmx_utils
from database import get_session
from database.schedules import crud
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from forms import schedules as schedules_forms
from services import schedules as schedules_service
from sqlmodel import Session

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_schedules_context(db: Session) -> dict:
    return {"schedules": crud.get_list(db)}


@router.get("/", response_class=HTMLResponse)
async def get_schedules(request: Request, db: Session = Depends(get_session)):
    context = get_schedules_context(db)
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
    db: Session = Depends(get_session),
):
    context = {
        "errors": {},
        "schedule": crud.get_by_id(db, schedule_id),
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
    db: Session = Depends(get_session),
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

    schedule = schedules_service.create_schedule(db, form.validated_model)

    context = {
        "schedule": schedule,
        "action": "created",
        **get_schedules_context(db),
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
    db: Session = Depends(get_session),
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

    schedule = schedules_service.edit_schedule(
        db=db,
        input_schedule=form.validated_model,
        schedule_id=schedule_id,
    )

    context = {
        "schedule": schedule,
        "action": "edited",
        **get_schedules_context(db),
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
