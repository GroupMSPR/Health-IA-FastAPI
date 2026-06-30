from datetime import date
from pathlib import Path

import joblib
import numpy as np

from app.response import ExercisePredictionOutput
from app.user import User

MODELS_DIR = Path(__file__).parent.parent / 'models'

class ExercisePredictionService:
    """Init the exercise recomendation AI"""
    def __init__(self):
        self.model   = joblib.load(MODELS_DIR / 'model.pkl')
        self.encoder = joblib.load(MODELS_DIR / 'encoder.pkl')

    @staticmethod
    def calculate_age(birth_date: date) -> int:
        today = date.today()

        return (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

    @staticmethod
    def map_physical_activity_level(physical_activity_level: str):
        match (physical_activity_level):
            case "sedentary":
                return 0
            case "moderate":
                return 1
            case "active":
                return 2
            case _:
                return -1

    @staticmethod
    def map_favorite_exercise_category(favorite_exercise_categorie: str):
        match (favorite_exercise_categorie.lower()):
            case "poids du corps":
                return 0
            case "musculation":
                return 1
            case "cardio":
                return 2
            case _:
                return -1

    def predict(self, user: User) -> ExercisePredictionOutput:
        X = np.array([[
                self.map_physical_activity_level(user.physical_activity_level),
                user.bmi,
                self.calculate_age(user.birthdate),
                self.map_favorite_exercise_category(user.favorite_exercise_category)
            ]])

        probabilities = self.model.predict_proba(X)[0]

        classes = self.model.classes_

        predictions_list = []
        for class_idx, confidence in zip(classes, probabilities):
            exercise_name = self.encoder.inverse_transform([[class_idx]])[0]
            predictions_list.append({
                'exercise': exercise_name,
                'confidence': round(float(confidence), 3)
            })

        predictions_list.sort(key=lambda x: x['confidence'], reverse=True)

        from app.response import ExercisePrediction
        return ExercisePredictionOutput(
            predictions=[ExercisePrediction(**pred) for pred in predictions_list]
        )
