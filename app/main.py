from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import cat, schedules, shopping, tasks

app = FastAPI()

app.include_router(tasks.router, tags=["tasks"])
app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
app.include_router(shopping.router, prefix="/shopping", tags=["shopping"])
app.include_router(cat.router, prefix="/cat", tags=["cat"])

app.mount("/static", StaticFiles(directory="static"), name="static")
