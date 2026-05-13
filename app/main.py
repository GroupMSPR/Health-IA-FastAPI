from fastapi import FastAPI

app = FastAPI(
    title="HealthAI Coach - API IA",
    description="API de traitement d'images et recommandations via LLaVA",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "API IA Opérationnelle sur le port 4000"}