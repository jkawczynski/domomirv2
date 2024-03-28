from pydantic import BaseModel


class AppRoute(BaseModel):
    name: str
    path: str
    emoji_icon: str


class ExternalAppRoute(BaseModel):
    name: str
    url: str
