import logging

from config import get_settings

from database import get_session
from integrations.mqtt.client import MQTTClient
from tasks.crud import TaskCrud
from tkq import DEFAULT_SCHEDULE_ARGS, broker

logger = logging.getLogger(__name__)


@broker.task(
    schedule=[
        {"cron": "0 7 * * *", **DEFAULT_SCHEDULE_ARGS},
        {"cron": "0 13 * * *", **DEFAULT_SCHEDULE_ARGS},
        {"cron": "0 17 * * *", **DEFAULT_SCHEDULE_ARGS},
        {"cron": "0 21 * * *", **DEFAULT_SCHEDULE_ARGS},
    ]
)
async def send_mqtt_remaining_tasks():
    session_maker = get_session()
    session = await anext(session_maker)
    crud = TaskCrud(session)

    count = await crud.get_unfinished_count()

    if count:
        settings = get_settings()
        client = MQTTClient(settings.mqtt)
        client.send_remaining_tasks(count)


@broker.task()
async def send_mqtt_task_assigned(task_id: int):
    session_maker = get_session()
    session = await anext(session_maker)
    crud = TaskCrud(session)
    logger.info(f"sending mqtt msg for assigned task, {task_id=}")
    task = await crud.get_by_id(task_id)
    if not task:
        return

    settings = get_settings()
    client = MQTTClient(settings.mqtt)
    client.send_task_assigned(task)
