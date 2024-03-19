import logging

from celery_app import app, get_settings
from database import engine
from database.tasks import crud
from integrations.mqtt.client import MQTTClient
from sqlmodel import Session

logger = logging.getLogger(__name__)


@app.task
def send_mqtt_remaining_tasks():
    with Session(engine) as db:
        count = crud.get_unfinished_count(db)

        if count:
            settings = get_settings()
            client = MQTTClient(settings.mqtt)
            client.send_remaining_tasks(count)
        else:
            print("no tasks")


@app.task
def send_mqtt_task_assigned(task_id: int):
    with Session(engine) as db:
        logger.info("sending mqtt msg for assigned task")
        task = crud.get_by_id(db, task_id)
        if not task:
            return

        settings = get_settings()
        client = MQTTClient(settings.mqtt)
        client.send_task_assigned(task)
