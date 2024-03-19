import logging

from celery import current_app
from celery.schedules import crontab
from config import get_settings

logger = logging.getLogger(__name__)


def create_celery():
    from integrations.mqtt import tasks  # noqa
    from integrations.wastes import tasks  # noqa
    from tasks import tasks  # noqa

    app = current_app
    app.config_from_object(get_settings().celery)
    app.conf.beat_schedule = {
        "tasks-and-schedules-cleanup": {
            "task": "tasks.tasks.clean_finished_tasks_and_schedules",
            "schedule": crontab(minute=0, hour=2),
        },
        "create-daily-tasks": {
            "task": "tasks.tasks.create_tasks_for_today",
            "schedule": crontab(minute=0, hour=2),
        },
        "create-prepare-waste-tasks": {
            "task": "integrations.wastes.tasks.create_task_to_prepare_wastes",
            "schedule": crontab(minute=0, hour=2),
        },
        "send-mqtt-msg-remaining-tasks-morning": {
            "task": "integrations.mqtt.tasks.send_mqtt_remaining_tasks",
            # Daily at 6:30
            "schedule": crontab(minute=30, hour=6),
        },
        "send-mqtt-msg-remaining-tasks-afternoon": {
            "task": "integrations.mqtt.tasks.send_mqtt_remaining_tasks",
            # Daily at 17
            "schedule": crontab(minute=0, hour=17),
        },
        "send-mqtt-msg-remaining-tasks-before-night": {
            "task": "integrations.mqtt.tasks.send_mqtt_remaining_tasks",
            # Daily at 17
            "schedule": crontab(minute=0, hour=21),
        },
    }

    return app
