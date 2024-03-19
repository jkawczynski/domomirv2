from pydantic_core import ErrorDetails


def parse_errors(errors: list[ErrorDetails]) -> dict:
    result = {}
    for error in errors:
        loc = ".".join(error["loc"])
        if not loc:
            loc = "_FORM"

        result[loc] = error["msg"]

    return result
