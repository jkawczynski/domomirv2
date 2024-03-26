from config import get_settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from cat import routes as cat_routes
from recipes import routes as recipes_routes
from schedules import routes as schedules_routes
from shopping import routes as shopping_routes
from tasks import routes as tasks_routes

settings = get_settings()

app = FastAPI()

app.include_router(tasks_routes.router, tags=["tasks"])
app.include_router(schedules_routes.router, prefix="/schedules", tags=["schedules"])
app.include_router(shopping_routes.router, prefix="/shopping", tags=["shopping"])
app.include_router(recipes_routes.router, prefix="/recipes", tags=["recipes"])
app.include_router(cat_routes.router, prefix="/cat", tags=["cat"])

app.mount("/static", StaticFiles(directory="static"), name="static")

if settings.serve_local_images:
    app.mount(
        settings.local_images_url, StaticFiles(directory="upload/images"), name="images"
    )
