# backend/app/schemas.py
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, conint

def _cfg():
    return {"from_attributes": True}

class CoachBase(BaseModel):
    username: str
    name: str
    surname: str
    birthday: date
    level: str

class CoachCreate(CoachBase):
    password: str

class Coach(CoachBase):
    id: int
    model_config = _cfg()

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: int
    coach_id: int
    model_config = _cfg()

class ChildBase(BaseModel):
    name: str
    surname: str
    birthday: date

class ChildCreate(ChildBase):
    pass

class Child(ChildBase):
    id: int
    group_id: int
    model_config = _cfg()

Score = conint(ge=0, le=10)

class ResultBase(BaseModel):
    participated: bool
    criteria1: Score
    criteria2: Score
    criteria3: Score
    criteria4: Score
    criteria5: Score

class ResultCreate(ResultBase):
    child_id: int

class Result(ResultBase):
    id: int
    child_id: int
    competition_id: int
    model_config = _cfg()

class CompetitionBase(BaseModel):
    date: date

class CompetitionCreate(CompetitionBase):
    group_id: int

class Competition(CompetitionBase):
    id: int
    group_id: int
    coach_id: int
    results: List[Result] = []
    model_config = _cfg()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    coach_id: Optional[int] = None
