from pydantic import ValidationError

from common.forms import Form
from recipes import models


class RecipeCreateForm(Form[models.RecipeCreate]):
    model = models.RecipeCreate

    def __init__(self, *args, **kwargs) -> None:
        self.images_ids = []
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        amount_and_units = self.form_data.pop("amount_and_unit")
        ingredients = self.form_data.pop("ingredient")

        self.form_data["ingredients"] = [
            {"name": name, "amount_and_unit": aau}
            for name, aau in zip(ingredients, amount_and_units, strict=False)
            if name
        ]
        if "images" in self.form_data:
            if isinstance(self.form_data["images"], list):
                self.images_ids = [
                    int(img_id) for img_id in self.form_data.pop("images")
                ]
            else:
                self.images_ids = [int(self.form_data["images"])]

        self._add_empty_ingredients()

    def _add_empty_ingredients(self):
        for _ in range(3):
            self.form_data["ingredients"].append({"name": "", "amount_and_unit": ""})


class IngredientsIdsForm(Form[models.RecipeIngredientsIds]):
    model = models.RecipeIngredientsIds

    def _clean_form_data(self):
        super()._clean_form_data()

        ingredients = self.form_data.get("ingredients")
        if not ingredients:
            raise ValidationError.from_exception_data("No ingredients provided", [])

        if isinstance(ingredients, list):
            self.form_data["ingredients"] = [int(ing_id) for ing_id in ingredients]
        else:
            self.form_data["ingredients"] = [int(ingredients)]
