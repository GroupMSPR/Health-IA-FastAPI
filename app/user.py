from datetime import date

from pydantic import BaseModel


class User(BaseModel):
    physical_activity_level: str
    bmi: float
    birthdate: date
    favorite_exercice_categorie: str
