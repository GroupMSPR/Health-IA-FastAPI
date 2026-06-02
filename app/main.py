import base64
import os
import io

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

app = FastAPI(
    title="HealthAI Coach - API IA",
    description="API de traitement d'images et recommandations via LLaVA",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {"message": "API IA Opérationnelle sur le port 4000"}


# Endpoint pour le traitement d'images
@app.post("/analyze-meal")
async def analyze_meal(image: UploadFile = File(...)):
    """Endpoint pour analyser une image de repas et obtenir des recommandations. (model llava)"""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")

    try:
        image_bytes = await image.read()
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            
            if pil_img.mode in ("RGBA", "P"):
                pil_img = pil_img.convert("RGB")
                
            pil_img.thumbnail((800, 800))
            
            compressed_buffer = io.BytesIO()
            pil_img.save(compressed_buffer, format="JPEG", optimize=True, quality=70)
            
            compressed_bytes = compressed_buffer.getvalue()
            
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Erreur lors de la lecture/compression de l'image: {str(e)}")
        image_base64 = base64.b64encode(compressed_bytes).decode("utf-8")

        prompt = """
        Tu es un expert en nutrition. 
        Analyse cette image de repas. 
        Identifie les aliments présents et donne une estimation calories et liste les macronutriments principaux (Protéines, Glucides, Lipides...). 
        Ensuite, propose des recommandations pour équilibrer ce repas si nécessaire.
        """

        payload = {
            "model": "llava",
            "prompt": prompt,
            "image": [image_base64],
            "stream": False,
            "temperature": 0.4,
            "max_tokens": 800,
        }

        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
        response.raise_for_status()

        result = response.json()
        return {
            "status": "success",
            "model_used": result.get("model"),
            "analysis": result.get("response"),
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503, detail=f"Erreur de communication avec Ollama: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
