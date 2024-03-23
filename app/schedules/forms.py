from common.forms import Form
from schedules import models


class ScheduleForm(Form[models.ScheduleCreate]):
    model = models.ScheduleCreate
