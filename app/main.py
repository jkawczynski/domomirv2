from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import cat, schedules, tasks, users

app = FastAPI()


app.include_router(tasks.router, tags=["tasks"])
app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(cat.router, prefix="/cat", tags=["cat"])


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
