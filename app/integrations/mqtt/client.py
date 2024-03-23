import json
import logging
from enum import Enum

import paho.mqtt.client as mqtt
from config import MqttSettings

from tasks import models

logger = logging.getLogger(__name__)


class Topic(Enum):
    TASKS_REMAINING = "tasks_remaining"
    TASK_ASSIGNED = "task_assigned"


class MQTTClient:
    def __init__(self, settings: MqttSettings) -> None:
        self.settings = settings
        if not self.settings.enabled:
            raise ValueError("MQTT is not enabled in settings")

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.settings.user and self.settings.password:
            self.client.username_pw_set(self.settings.user, self.settings.password)

    def _send_message(self, topic: Topic, payload: mqtt.PayloadType):
        if not self.settings.host:
            raise ValueError("MQTT_HOST must be set in settings for MQTT")

        self.client.connect(self.settings.host, self.settings.port)
        publish_topic = f"{self.settings.topic_prefix}/{topic.value}"
        self.client.publish(publish_topic, payload)
        self.client.disconnect()

    def send_remaining_tasks(self, num_tasks: int):
        self._send_message(Topic.TASKS_REMAINING, num_tasks)

    def send_task_assigned(self, task: models.Task):
        assigned_to = task.assigned_to
        if not assigned_to:
            raise ValueError("`assigned_to` must be set on task")

        payload = {
            "task": task.name,
            "assigned_to": assigned_to.name,
        }
        self._send_message(Topic.TASK_ASSIGNED, json.dumps(payload))
