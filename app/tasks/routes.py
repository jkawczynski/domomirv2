from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from templates import templates

from common import htmx_utils
from database import get_session
from tasks import crud, forms, services
from users import crud as users_crud

router = APIRouter()


async def get_tasks_context(session: AsyncSession) -> dict:
    tasks = await crud.get_list(session)
    users = await users_crud.get_list(session)
    return {
        "tasks": tasks,
        "users": users,
        "all_completed": all(task.completed for task in tasks),
        "partially_completed": len([task for task in tasks if task.completed]),
    }


@router.get("/", response_class=HTMLResponse)
async def get_tasks(request: Request, session: AsyncSession = Depends(get_session)):
    context = await get_tasks_context(session)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/index.html",
        full_template="tasks/index.html",
    )


@router.post("/tasks", response_class=HTMLResponse)
async def create_task(
    request: Request,
    form_data: Annotated[dict, Body()],
    session: AsyncSession = Depends(get_session),
):
    form = forms.TaskFormCreate(form_data)
    if not form.is_valid():
        context = await get_tasks_context(session)
        context["errors"] = form.form_errors()
        return htmx_utils.template_response(
            request=request,
            templates=templates,
            context=context,
            partial_template="tasks/_partials/tasks_list.html",
            full_template="tasks/index.html",
        )

    task = form.validated_model
    await services.create_task(session, task)
    context = await get_tasks_context(session)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )


@router.patch("/tasks/{task_id}", response_class=HTMLResponse)
async def update_task(
    request: Request,
    task_id: int,
    form_data: Annotated[dict, Body()],
    session: AsyncSession = Depends(get_session),
):
    form = forms.TaskFormEdit(form_data)
    if not form.is_valid():
        context = await get_tasks_context(session)
        context["errors"] = form.form_errors()
        raise HTTPException(status_code=500, detail="unhandled")

    await services.update_task(session, task_id, form.validated_model)
    context = await get_tasks_context(session)
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="tasks/_partials/tasks_list.html",
        full_template="tasks/index.html",
    )
