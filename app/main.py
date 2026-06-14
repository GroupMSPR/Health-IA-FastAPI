import os
from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, UploadFile
from pymongo import MongoClient

from app.exercice import ExercicePredictionService
from app.food import guess_image
from app.user import User

app = FastAPI(
    title="HealthAI Coach - API IA",
    description="API de traitement d'images et recommandations via LLaVA",
    version="1.0.0",
)

eps = ExercicePredictionService()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongodb:27017/")
client = MongoClient(MONGO_URI)
db = client.healthai
exercise_recommendations_col = db.exercise_recomendation
food_recomendation = db.food_recomendation

@app.get("/")
def read_root():
    return {"message": "API IA Opérationnelle sur le port 4000"}

@app.post("/analyze-meal")
async def analyze_meal(image: UploadFile = File(...)):
    """Analyse une image de repas → données nutritionnelles structurées (LLaVA)."""
    return await guess_image(image)

@app.post("/recommend")
def get_exercices(user: User):
    """get a list of all exercice with ai probability"""
    try: 
        prediction_output = eps.predict(user)

        doc_to_insert = {
            "user_profile": user.model_dump(mode="json"),
            "recommendations": [p.model_dump(mode="json") for p in prediction_output.predictions[:10]],
            "created_at": datetime.now(timezone.utc)
        }

        exercise_recommendations_col.insert_one(doc_to_insert)

        return prediction_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
