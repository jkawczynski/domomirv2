import logging

from celery import shared_task
from config import get_settings
from database import engine
from database.tasks import crud
from integrations.mqtt.client import MQTTClient
from sqlmodel import Session

logger = logging.getLogger(__name__)


@shared_task
def send_mqtt_remaining_tasks():
    with Session(engine) as db:
        count = crud.get_unfinished_count(db)

        if count:
            settings = get_settings()
            client = MQTTClient(settings.mqtt)
            client.send_remaining_tasks(count)


@shared_task
def send_mqtt_task_assigned(task_id: int):
    with Session(engine) as db:
        logger.info(f"sending mqtt msg for assigned task, {task_id=}")
        task = crud.get_by_id(db, task_id)
        if not task:
            return

        settings = get_settings()
        client = MQTTClient(settings.mqtt)
        client.send_task_assigned(task)
