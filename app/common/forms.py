from typing import Annotated, Generic, TypeVar

from common.errors import parse_errors
from fastapi import Body
from pydantic import ValidationError
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class FormDataValidationError(Exception):
    def __init__(self, validation_error: ValidationError):
        self.validation_error = validation_error


class Form(Generic[T]):
    model: type[T]
    _validated_model: T

    def __init__(
        self,
        form_data: Annotated[dict, Body()],
        skip_empty_strings: bool = True,
    ) -> None:
        super().__init__()
        self.skip_empty_strings = skip_empty_strings
        self.form_data = form_data
        self._clean_form_data()

    def _clean_form_data(self):
        if self.skip_empty_strings:
            self._convert_empty_strings_to_none()

    def _convert_empty_strings_to_none(self):
        for key in self.form_data:
            if self.form_data[key] == "":
                self.form_data[key] = None

    def is_valid(self) -> bool:
        try:
            self._validated_model = self.model.model_validate(self.form_data)
            return True
        except ValidationError as exc:
            self.validation_error = exc
            return False

    def form_errors(self) -> dict:
        return parse_errors(self.validation_error.errors())

    @property
    def validated_model(self) -> T:
        if not self._validated_model:
            raise ValueError("Call `is_valid` first")

        return self._validated_model
