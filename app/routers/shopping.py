from common import htmx_utils
from database import get_session
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_session)):
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context={},
        partial_template="shopping/_partials/index.html",
        full_template="shopping/index.html",
    )
