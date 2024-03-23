from common.forms import Form
from tasks import models


class TaskFormCreate(Form[models.TaskCreate]):
    model = models.TaskCreate


class TaskFormEdit(Form[models.TaskEdit]):
    model = models.TaskEdit

    def _clean_form_data(self):
        super()._clean_form_data()
        if "completed" not in self.form_data:
            return

        self.form_data["completed"] = int(self.form_data["completed"])
