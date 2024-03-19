from common.forms import Form
from database.schedules import models


class ScheduleForm(Form[models.ScheduleCreate]):
    model = models.ScheduleCreate
