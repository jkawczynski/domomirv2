import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from common import htmx_utils

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class Cat(BaseModel):
    id: str
    url: str
    width: int
    height: int


async def get_random_cat() -> Cat:
    url = "https://api.thecatapi.com/v1/images/search"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    return Cat(**response.json()[0])


@router.get("", response_class=HTMLResponse)
async def index(request: Request):
    context = {"cat": await get_random_cat()}
    return htmx_utils.template_response(
        request=request,
        templates=templates,
        context=context,
        partial_template="cat/_partials/index.html",
        full_template="cat/index.html",
    )
