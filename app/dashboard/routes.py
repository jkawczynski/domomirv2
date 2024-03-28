from config import get_settings
from dashboard import models
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from templates import templates

from common import htmx_utils

settings = get_settings()


router = APIRouter()

apps: list[models.AppRoute] = [
    models.AppRoute(name="Daily tasks", path="/tasks", emoji_icon="✅"),
    models.AppRoute(name="Shopping list", path="/shopping", emoji_icon="🛒"),
    models.AppRoute(name="Recipes", path="/recipes", emoji_icon="🍲"),
]


def get_external_apps() -> list[models.ExternalAppRoute]:
    names = settings.external_apps_names
    urls = settings.external_apps_urls

    return [
        models.ExternalAppRoute(name=name, url=url)
        for name, url in zip(names, urls, strict=False)
    ]


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={"apps": apps, "external_apps": get_external_apps()},
        partial_template="dashboard/_partials/index.html",
        full_template="dashboard/index.html",
    )
