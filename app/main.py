
from app.exercice import ExercicePredictionService
from app.food import guess_image
from app.user import User
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(
    title="HealthAI Coach - API IA",
    description="API de traitement d'images et recommandations via LLaVA",
    version="1.0.0",
)

eps = ExercicePredictionService()
    
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
        return eps.predict(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))