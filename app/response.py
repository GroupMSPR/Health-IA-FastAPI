
from pydantic import BaseModel


class ExercisePrediction(BaseModel):
    exercise:    str
    confidence: float

class ExercisePredictionOutput(BaseModel):
    predictions: list[ExercisePrediction]
