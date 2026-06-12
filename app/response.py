
from pydantic import BaseModel


class ExercicePrediction(BaseModel):
    exercice:    str
    confidence: float

class ExercicePredictionOutput(BaseModel):
    predictions: list[ExercicePrediction]
