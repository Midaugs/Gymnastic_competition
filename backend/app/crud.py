# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_coach_by_username(db: Session, username: str):
    return db.query(models.Coach).filter(models.Coach.username == username).first()

def get_coach_by_name(db: Session, name: str, surname: str):
    return db.query(models.Coach).filter(models.Coach.name == name, models.Coach.surname == surname).first()

def create_coach(db: Session, coach: schemas.CoachCreate):
    if get_coach_by_username(db, coach.username):
        raise ValueError("Username already exists")
    hashed_password = pwd_context.hash(coach.password)
    db_coach = models.Coach(
        username=coach.username,
        name=coach.name,
        surname=coach.surname,
        birthday=coach.birthday,
        level=coach.level,
        password_hash=hashed_password,
    )
    db.add(db_coach)
    db.commit()
    db.refresh(db_coach)
    return db_coach

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_coach(db: Session, username: str, password: str):
    coach = get_coach_by_username(db, username)
    if not coach or not verify_password(password, coach.password_hash):
        return None
    return coach

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)