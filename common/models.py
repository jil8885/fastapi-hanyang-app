from pydantic import BaseModel


class ShuttleRequest(BaseModel):
    busStop: str


class CampusRequest(BaseModel):
    campus: str


class BusRequest(BaseModel):
    campus: str
    route: str


class MenuRequest(BaseModel):
    campus: str
    restaurant: str


class LanguageRequest(BaseModel):
    language: str
