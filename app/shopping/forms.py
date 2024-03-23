from datetime import datetime

from common.forms import Form
from shopping import models


class ShoppingListItemFormCreate(Form[models.ShoppingListItemCreate]):
    model = models.ShoppingListItemCreate


class ShoppingListItemFormEdit(Form[models.ShoppingListItemEdit]):
    model = models.ShoppingListItemEdit

    def _clean_form_data(self):
        super()._clean_form_data()
        if "completed" not in self.form_data:
            return

        is_completed = int(self.form_data["completed"])
        self.form_data["completed"] = datetime.now() if is_completed else None
