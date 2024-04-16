from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from templates import templates

from common import htmx_utils
from tasks import forms
from tasks.crud import TaskCrud
from tasks.services import TaskService
from users.crud import UserCrud

router = APIRouter()


async def get_tasks_context(
    crud: TaskCrud = Depends(TaskCrud), user_crud: UserCrud = Depends(UserCrud)
) -> dict:
    tasks = await crud.get_list()
    users = await user_crud.get_list()
    return {
        "tasks": tasks,
        "users": users,
        "all_completed": all(task.completed for task in tasks),
        "partially_completed": len([task for task in tasks if task.completed]),
    }


@router.get("", response_class=HTMLResponse)
async def index(
    request: Request,
    context: Annotated[dict, Depends(get_tasks_context)],
):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/index.html",
        full_template="tasks/index.html",
    )


@router.post("", response_class=HTMLResponse)
async def create_task(
    request: Request,
    form_data: Annotated[dict, Body()],
    crud: TaskCrud = Depends(TaskCrud),
    user_crud: UserCrud = Depends(UserCrud),
    service: TaskService = Depends(TaskService),
):
    form = forms.TaskFormCreate(form_data)
    if not form.is_valid():
        context = await get_tasks_context(crud, user_crud)
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="tasks/_partials/tasks_list.html",
            full_template="tasks/index.html",
        )

    task = form.validated_model
    await service.create_task(task)
    context = await get_tasks_context(crud, user_crud)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )


@router.patch("/{task_id}", response_class=HTMLResponse)
async def update_task(
    request: Request,
    task_id: int,
    form_data: Annotated[dict, Body()],
    crud: TaskCrud = Depends(TaskCrud),
    user_crud: UserCrud = Depends(UserCrud),
    service: TaskService = Depends(TaskService),
):
    form = forms.TaskFormEdit(form_data)
    if not form.is_valid():
        context = await get_tasks_context(crud, user_crud)
        context["errors"] = form.form_errors()
        raise HTTPException(status_code=500, detail="unhandled")

    await service.update_task(task_id, form.validated_model)
    context = await get_tasks_context(crud, user_crud)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )
