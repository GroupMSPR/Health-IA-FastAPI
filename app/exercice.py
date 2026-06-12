from datetime import date
from pathlib import Path

import joblib
import numpy as np

from app.response import ExercicePredictionOutput
from app.user import User

MODELS_DIR = Path(__file__).parent.parent / 'models'

class ExercicePredictionService:
    """Init the exercice recomendation AI"""
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

    @staticmethod
    def map_favorite_exercice_categorie(favorite_exercice_categorie: str):
        match (favorite_exercice_categorie):
            case "Poids du corps":
                return 0
            case "Musculation":
                return 1
            case "Cardio":
                return 2

    def predict(self, user: User) -> ExercicePredictionOutput:
        X = np.array([[
                self.map_physical_activity_level(user.physical_activity_level),
                user.bmi,
                self.calculate_age(user.birthdate),
                self.map_favorite_exercice_categorie(user.favorite_exercice_categorie)
            ]])

        # Get probabilities for all classes
        probabilities = self.model.predict_proba(X)[0]

        # Get all class labels (numeric indices)
        classes = self.model.classes_

        # Create list of (exercice, confidence) sorted by confidence descending
        predictions_list = []
        for class_idx, confidence in zip(classes, probabilities):
            # Convert numeric index back to exercise name using encoder
            exercice_name = self.encoder.inverse_transform([[class_idx]])[0]
            predictions_list.append({
                'exercice': exercice_name,
                'confidence': round(float(confidence), 3)
            })

        # Sort by confidence descending
        predictions_list.sort(key=lambda x: x['confidence'], reverse=True)

        from app.response import ExercicePrediction
        return ExercicePredictionOutput(
            predictions=[ExercicePrediction(**pred) for pred in predictions_list]
        )
