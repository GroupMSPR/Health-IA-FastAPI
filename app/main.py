import os
from datetime import UTC, datetime

from fastapi import FastAPI, File, HTTPException, UploadFile
from pymongo import MongoClient

from app.exercise import ExercisePredictionService
from app.food import guess_image
from app.user import User

app = FastAPI(
    title="HealthAI Coach - API IA",
    description="API de traitement d'images et recommandations via LLaVA",
    version="1.0.0",
)

eps = ExercisePredictionService()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongodb:27017/")
client = MongoClient(MONGO_URI)
db = client.healthai
exercise_recommendations = db.exercise_recomendation
food_recomendation = db.food_recomendation

@app.get("/")
def read_root():
    return {"message": "API IA Opérationnelle sur le port 4000"}

@app.post("/analyze-meal")
async def analyze_meal(image: UploadFile = File(...)):
    """Analyse une image de repas → données nutritionnelles structurées (LLaVA)."""
    image_result = await guess_image(image)
    
    doc_to_insert = {
        "status": image_result["status"],
        "data": image_result["data"]
    }
    
    food_recomendation.insert_one(doc_to_insert)

    return image_result

@app.post("/recommend")
def get_exercises(user: User):
    """get a list of all exercise with ai probability"""
    try: 
        prediction_output = eps.predict(user)

        doc_to_insert = {
            "user_profile": user.model_dump(mode='json'),
            "recommendations": [p.model_dump() for p in prediction_output.predictions[:10]],
            "created_at": datetime.now(UTC)
        }

        exercise_recommendations.insert_one(doc_to_insert)

        return prediction_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
