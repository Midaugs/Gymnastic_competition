# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from . import models, schemas, crud, database
from .deps import get_db, get_current_coach
from .pdf_utils import generate_results_pdf

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Gymnastic Competition Results API")

# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5501", "http://localhost:5501",
        "http://127.0.0.1:5500", "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ---------- Auth ----------
@app.post("/register/", response_model=schemas.Coach, status_code=201)
def register(coach: schemas.CoachCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_coach(db, coach)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/token", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form.username = username
    user = crud.authenticate_coach(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = crud.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}

# ---------- Groups ----------
@app.post("/groups/", response_model=schemas.Group, status_code=201)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    exists = db.query(models.Group).filter(models.Group.name == group.name, models.Group.coach_id == me.id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Group name already exists for this coach")
    db_group = models.Group(name=group.name, coach_id=me.id)
    db.add(db_group); db.commit(); db.refresh(db_group)
    return db_group

@app.get("/groups/", response_model=List[schemas.Group])
def list_groups(db: Session = Depends(get_db), me=Depends(get_current_coach)):
    return db.query(models.Group).filter(models.Group.coach_id == me.id).order_by(models.Group.name).all()

@app.delete("/groups/{group_id}", status_code=204)
def delete_group(group_id: int, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    g = db.query(models.Group).filter(models.Group.id == group_id, models.Group.coach_id == me.id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(g); db.commit()
    return

# ---------- Children ----------
@app.post("/groups/{group_id}/children/", response_model=schemas.Child, status_code=201)
def add_child(group_id: int, child: schemas.ChildCreate, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    g = db.query(models.Group).filter(models.Group.id == group_id, models.Group.coach_id == me.id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    db_child = models.Child(**child.dict(), group_id=group_id)
    db.add(db_child); db.commit(); db.refresh(db_child)
    return db_child

@app.get("/groups/{group_id}/children/", response_model=List[schemas.Child])
def list_children(group_id: int, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    g = db.query(models.Group).filter(models.Group.id == group_id, models.Group.coach_id == me.id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    return db.query(models.Child).filter(models.Child.group_id == group_id).order_by(models.Child.surname, models.Child.name).all()

@app.delete("/children/{child_id}", status_code=204)
def delete_child(child_id: int, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    c = db.query(models.Child).join(models.Group, models.Child.group_id == models.Group.id)\
         .filter(models.Child.id == child_id, models.Group.coach_id == me.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Child not found")
    db.delete(c); db.commit()
    return

# ---------- Competitions ----------
@app.post("/competitions/", response_model=schemas.Competition, status_code=201)
def create_competition(payload: schemas.CompetitionCreate, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    g = db.query(models.Group).filter(models.Group.id == payload.group_id, models.Group.coach_id == me.id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    comp = models.Competition(date=payload.date, group_id=payload.group_id, coach_id=me.id)
    db.add(comp); db.commit(); db.refresh(comp)
    return comp

@app.get("/competitions/", response_model=List[schemas.Competition])
def list_competitions(db: Session = Depends(get_db), me=Depends(get_current_coach)):
    return db.query(models.Competition).filter(models.Competition.coach_id == me.id)\
             .order_by(models.Competition.date.desc()).all()

@app.delete("/competitions/{competition_id}", status_code=204)
def delete_competition(competition_id: int, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    comp = db.query(models.Competition).filter(models.Competition.id == competition_id,
                                               models.Competition.coach_id == me.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    db.delete(comp); db.commit()
    return

# ---------- Results ----------
@app.post("/competitions/{competition_id}/results/", response_model=List[schemas.Result], status_code=201)
def upsert_results(competition_id: int, results: List[schemas.ResultCreate], db: Session = Depends(get_db), me=Depends(get_current_coach)):
    comp = db.query(models.Competition).filter(models.Competition.id == competition_id,
                                               models.Competition.coach_id == me.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Validate children belong to the competition's group
    group_child_ids = {c.id for c in db.query(models.Child).filter(models.Child.group_id == comp.group_id).all()}
    db_results: list[models.Result] = []
    for r in results:
        if r.child_id not in group_child_ids:
            raise HTTPException(status_code=400, detail=f"Child {r.child_id} not in competition group")
        # Upsert (update if exists else create)
        existing = db.query(models.Result).filter(models.Result.competition_id == competition_id,
                                                  models.Result.child_id == r.child_id).first()
        if existing:
            for k, v in r.dict().items():
                setattr(existing, k, v)
            db_results.append(existing)
        else:
            new_r = models.Result(competition_id=competition_id, **r.dict())
            db.add(new_r)
            db_results.append(new_r)
    db.commit()
    for rr in db_results: db.refresh(rr)
    return db_results

@app.get("/competitions/{competition_id}/results/", response_model=List[schemas.Result])
def get_results(competition_id: int, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    comp = db.query(models.Competition).filter(models.Competition.id == competition_id,
                                               models.Competition.coach_id == me.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    return db.query(models.Result).filter(models.Result.competition_id == competition_id)\
             .order_by(models.Result.id).all()

# ---------- PDF ----------
@app.get("/competitions/{competition_id}/pdf/")
def competition_pdf(competition_id: int, db: Session = Depends(get_db), me=Depends(get_current_coach)):
    comp = db.query(models.Competition).filter(models.Competition.id == competition_id,
                                               models.Competition.coach_id == me.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    group = db.query(models.Group).filter(models.Group.id == comp.group_id).first()
    children = db.query(models.Child).filter(models.Child.group_id == group.id).order_by(models.Child.surname, models.Child.name).all()
    results = db.query(models.Result).filter(models.Result.competition_id == competition_id).all()
    pdf = generate_results_pdf(comp, group, me, children, results)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="competition_{competition_id}_results.pdf"'})
