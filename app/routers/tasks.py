from typing import Annotated

from common import htmx_utils
from database import get_session
from database.tasks import crud
from database.users import crud as users_crud
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from forms import tasks as tasks_forms
from services import tasks as tasks_service
from sqlmodel import Session

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_tasks_context(db: Session) -> dict:
    tasks = crud.get_list(db)
    users = users_crud.get_list(db)
    return {
        "tasks": tasks,
        "users": users,
        "all_completed": all(task.completed for task in tasks),
        "partially_completed": len([task for task in tasks if task.completed]),
    }


@router.get("/", response_class=HTMLResponse)
async def get_tasks(request: Request, db: Session = Depends(get_session)):
    context = get_tasks_context(db)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/index.html",
        full_template="tasks/index.html",
    )


@router.post("/tasks/create", response_class=HTMLResponse)
async def create_task(
    request: Request,
    form_data: Annotated[dict, Body()],
    db: Session = Depends(get_session),
):
    form = tasks_forms.TaskForm(form_data)
    if not form.is_valid():
        context = get_tasks_context(db)
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="tasks/_partials/tasks_list.html",
            full_template="tasks/index.html",
        )

    task = form.validated_model
    tasks_service.create_task(db, task)
    context = get_tasks_context(db)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )


@router.patch("/tasks/{task_id}/complete", response_class=HTMLResponse)
async def complete_task(
    request: Request,
    task_id: int,
    db: Session = Depends(get_session),
):
    tasks_service.complete_task(db, task_id)
    context = get_tasks_context(db)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )


@router.patch("/tasks/{task_id}/undo-complete", response_class=HTMLResponse)
async def undo_complete_task(
    request: Request,
    task_id: int,
    db: Session = Depends(get_session),
):
    tasks_service.undo_complete_task(db, task_id)
    context = get_tasks_context(db)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )


@router.patch("/tasks/{task_id}/assign/{user_id}", response_class=HTMLResponse)
async def assign_task(
    request: Request,
    task_id: int,
    user_id: int,
    db: Session = Depends(get_session),
):
    tasks_service.assign_task(db, task_id, user_id)
    context = get_tasks_context(db)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )
