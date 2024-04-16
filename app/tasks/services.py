from datetime import datetime

from fastapi import Depends, HTTPException

from integrations.mqtt.tasks import send_mqtt_task_assigned
from schedules.tasks import update_schedule
from tasks import models
from tasks.crud import TaskCrud
from users.crud import UserCrud


class TaskService:
    def __init__(
        self,
        crud: TaskCrud = Depends(TaskCrud),
        user_crud: UserCrud = Depends(UserCrud),
    ) -> None:
        self.crud = crud
        self.user_crud = user_crud

    async def create_task(self, task: models.TaskCreate) -> None:
        db_task = models.Task.model_validate(task)
        await self.crud.persist(db_task)

    async def update_task(
        self,
        task_id: int,
        task: models.TaskEdit,
    ) -> None:
        db_task = await self.crud.get_by_id(task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = task.model_dump(exclude_defaults=True)
        await self._partial_update(db_task, update_data)

        # send background tasks
        if update_data.get("completed") and db_task.schedule_id:
            await update_schedule.kiq(db_task.schedule_id)

        if update_data.get("assigned_to_id") and db_task.assigned_to_id:
            await send_mqtt_task_assigned.kiq(db_task.id)

    async def _partial_update(self, db_task: models.Task, update_data: dict):
        if "completed" in update_data:
            db_task.completed = datetime.now() if update_data["completed"] else None

        if "assigned_to_id" in update_data:
            user = await self.user_crud.get_by_id(update_data["assigned_to_id"])
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            db_task.assigned_to = user

        await self.crud.persist(db_task)
