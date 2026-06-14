import os
import uuid

from dotenv import load_dotenv
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, relationship

load_dotenv()

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TMP_PATH = os.path.join(BASE_PATH, "tmp")
TO_IMPORT_ID = os.getenv("TO_IMPORT_ID")
ARCHIVE_ID = os.getenv("ARCHIVE_ID")
ERROR_ID = os.getenv("ERROR_ID")
LOG_ID = os.getenv("LOG_ID")

class Base(DeclarativeBase):
    pass

class Practice(Base):
    __tablename__ = "practice"

    practice_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(ForeignKey("users.user_id"))
    exercise_id = Column(ForeignKey("exercises.exercise_id"))
    practiced_at = Column(Date)

    user = relationship("User", back_populates="practices")
    exercise = relationship("Exercise", back_populates="practice")

class User(Base):
    __tablename__ = "users"

    user_id = Column(Uuid, primary_key=True, default=uuid.uuid4)

    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)

    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(50), nullable=False)

    profile_picture = Column(Text)

    birthdate = Column(Date, nullable=False)
    gender = Column(String(50), nullable=False)

    weight = Column(Numeric(15, 2), nullable=False)
    height = Column(Integer, nullable=False)
    bmi = Column(Numeric(15, 2), nullable=False)
    body_fat_pct = Column(Numeric(15, 2), nullable=False)

    physical_activity_level = Column(String(50), nullable=False)
    daily_caloric_intake = Column(Integer, nullable=False)

    favorite_exercice_categorie = Column(String)

    practices = relationship("Practice", back_populates="user")

class Exercise(Base) :

    __tablename__       = "exercises"

    exercise_id         = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name                = Column(String(50), nullable=False)
    type                = Column(String(50), nullable=False)
    difficulty_level    = Column(String(50), nullable=False)
    instructions        = Column(Text, nullable=False)
    short_description   = Column(String(50))
    category  = Column(String(50))
    sub_category  = Column(String(50))
    rep_range_min = Column(String(50))
    rep_range_max = Column(String(50))
    recommended_duration_seconds  = Column(String(50))
    recommended_rest_seconds  = Column(String(50))
    estimated_calories_per_minute = Column(String(50))
    range_of_motion   = Column(String(50))
    injury_risk_level = Column(String(50))
    next_progression_exercise = Column(String(50))
    previous_progression_exercise = Column(String(50))

    practice = relationship("Practice", back_populates="exercise")
