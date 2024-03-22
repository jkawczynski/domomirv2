from config import get_settings
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

settings = get_settings()


broker = ListQueueBroker(url=settings.taskiq.broker_url)
scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
DEFAULT_SCHEDULE_ARGS = {"cron_offset": "Europe/Warsaw"}
