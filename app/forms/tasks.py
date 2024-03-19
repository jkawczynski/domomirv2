from common.forms import Form
from database.tasks import models


class TaskForm(Form[models.TaskCreate]):
    model = models.TaskCreate
