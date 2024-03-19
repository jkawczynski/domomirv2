from database import get_session
from database.users import crud, models
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

router = APIRouter()


@router.post("/", response_model=models.User)
async def get_tasks(
    request: Request,
    user: models.UserCreate,
    db: Session = Depends(get_session),
):
    db_user = models.User.model_validate(user)
    return crud.persist(db, db_user)
