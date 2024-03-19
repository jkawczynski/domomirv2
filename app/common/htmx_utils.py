from fastapi import Request
from fastapi.templating import Jinja2Templates


def is_htmx_request(request: Request):
    return "hx-request" in request.headers


def template_response(
    request: Request,
    templates: Jinja2Templates,
    partial_template: str,
    full_template: str,
    **kwargs,
):
    if is_htmx_request(request):
        return templates.TemplateResponse(
            request=request, name=partial_template, **kwargs
        )

    return templates.TemplateResponse(request=request, name=full_template, **kwargs)
