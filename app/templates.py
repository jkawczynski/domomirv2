from config import get_settings
from fastapi.templating import Jinja2Templates

from common import filters

settings = get_settings()
templates = Jinja2Templates(
    directory="templates",
    context_processors=[lambda r: {"app_version": settings.app_version}],
)
templates.env.filters.update(filters.template_filters)
