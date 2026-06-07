import base64
import json
import os

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = "llava"
TIMEOUT = 120

app = FastAPI(
    title="HealthAI Coach - API IA",
    description="API de traitement d'images et recommandations via LLaVA",
    version="1.0.0",
)

def build_nutrition_prompt() -> str:
    return """You are a nutrition expert. Analyze the meal photo and respond with ONLY valid JSON, no markdown, no text outside JSON.

    RULES:
    - ALWAYS estimate nutritional values even if the image is imperfect. Never return -1 for nutrition fields.
    - Base estimates on the dish type and typical portion if visual cues are unclear.
    - Use -1 ONLY if the image contains no identifiable food at all.
    - confidence: integer 0-100 based on your actual analysis
    - allergens: only those actually present or very likely

    VALID ENUMS:
    - portion_type: "estimated_visible" | "standard_serving"
    - cooking_method: "raw" | "grilled" | "fried" | "baked" | "steamed" | "boiled" | "mixed" | "unknown"
    - meal_type: "breakfast" | "lunch" | "dinner" | "snack" | "dessert" | "drink" | "unknown"
    - flags: ["image_blurry", "partial_view", "multiple_dishes", "unusual_angle"]

    EXACT JSON STRUCTURE:
    {
    "name": "<dish name in english>",
    "portion_size_g": <estimate based on dish type, e.g. pasta=350, salad=250, burger=300>,
    "portion_type": "<enum>",
    "confidence": <integer>,
    "confidence_reason": "<your reason>",
    "alternatives": [{"name": "<alt dish>", "confidence": <integer>}],
    "flags": [],
    "cooking_method": "<enum>",
    "meal_type": "<enum>",
    "meal_tags": ["<tag>"],
    "allergens": ["<allergen if present>"],
    "nutrition": {
        "calories": <estimate for identified dish and portion>,
        "protein": <float>,
        "carbs": <float>,
        "fat": <float>,
        "saturated_fat": <float>,
        "fiber": <float>,
        "sugars": <float>,
        "sodium": <integer>,
        "cholesterol": <integer>
    }
    }"""

def extract_json(text: str):
    """Extrait et parse le JSON d'une réponse LLAVA, meme entouré de texte/```."""
    if not text:
        return None
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            return None
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return None        
    
@app.get("/")
def read_root():
    return {"message": "API IA Opérationnelle sur le port 4000"}

@app.post("/analyze-meal")
async def analyze_meal(image: UploadFile = File(...)):
    """Analyse une image de repas → données nutritionnelles structurées (LLaVA)."""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")

    #L'image arrive par le réseau -> on lit les octets et on encode en base64
    image_bytes = await image.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": MODEL_NAME,
        "prompt": build_nutrition_prompt(),
        "images": [image_base64],         
        "stream": False,
        "options": {"temperature": 0.1},   
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        raw = response.json().get("response", "")
        data = extract_json(raw)
    
        if data is not None:
            return {"status": "success", "is_working": 0, "data": data}

    except requests.exceptions.RequestException:
        pass 

    return {
        "status": "degraded",
        "is_working": 1,
        "data": None, 
        "message": "Analyse automatique impossible. Veuillez saisir les aliments manuellement."
    }