# backend/app/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Coach(Base):
    __tablename__ = "coaches"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)  # NEW
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    level = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    groups = relationship("Group", back_populates="coach", cascade="all, delete-orphan")
    competitions = relationship("Competition", back_populates="coach", cascade="all, delete-orphan")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    coach_id = Column(Integer, ForeignKey('coaches.id', ondelete="CASCADE"), nullable=False)

    coach = relationship("Coach", back_populates="groups")
    children = relationship("Child", back_populates="group", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('name', 'coach_id', name='uq_group_name_per_coach'),)

class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete="CASCADE"), nullable=False

    )
    group = relationship("Group", back_populates="children")
    results = relationship("Result", back_populates="child", cascade="all, delete-orphan")

class Competition(Base):
    __tablename__ = "competitions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete="CASCADE"), nullable=False)
    coach_id = Column(Integer, ForeignKey('coaches.id', ondelete="CASCADE"), nullable=False)

    group = relationship("Group")
    coach = relationship("Coach", back_populates="competitions")
    results = relationship("Result", back_populates="competition", cascade="all, delete-orphan")

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey('competitions.id', ondelete="CASCADE"), nullable=False)
    child_id = Column(Integer, ForeignKey('children.id', ondelete="CASCADE"), nullable=False)
    participated = Column(Boolean, default=True, nullable=False)
    criteria1 = Column(Integer, default=0, nullable=False)
    criteria2 = Column(Integer, default=0, nullable=False)
    criteria3 = Column(Integer, default=0, nullable=False)
    criteria4 = Column(Integer, default=0, nullable=False)
    criteria5 = Column(Integer, default=0, nullable=False)

    competition = relationship("Competition", back_populates="results")
    child = relationship("Child", back_populates="results")