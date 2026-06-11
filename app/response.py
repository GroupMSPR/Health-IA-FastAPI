from pydantic import BaseModel
from typing import List

class ExercicePrediction(BaseModel):
    exercice:    str
    confidence: float

class ExercicePredictionOutput(BaseModel):
    predictions: List[ExercicePrediction]