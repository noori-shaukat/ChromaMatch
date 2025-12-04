# src/api/main.py

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from src.rag.rag_pipeline import ChromaRAGPipeline
from src.models.chroma_model import analyze_image
import tempfile
import os

app = FastAPI(title="ChromaMatch")

rag_pipeline = ChromaRAGPipeline()


# ---------- HEALTH ----------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- ML ANALYSIS ----------
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Step 1: User uploads an image.
    Step 2: ML model analyzes skin tone, undertone, eyes, hair.
    """

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(await file.read())
    tmp.close()

    result = analyze_image(tmp.name)
    os.unlink(tmp.name)
    return result


# ---------- INPUT MODEL FOR RAG ----------
class PredictionInput(BaseModel):
    skin_tone: str
    tone_group: str | None = None
    descriptor: str | None = None
    undertone: str
    eye_color: str | list
    hair_color: str


# ---------- RAG RECOMMENDATION ----------
@app.post("/recommend")
async def recommend(preds: PredictionInput):
    """
    Takes ML predictions (from /analyze) and generates fashion/color recommendations.
    """

    # Convert pydantic model to dict
    preds_dict = preds.dict()

    # Generate recommendations
    result = rag_pipeline.recommend_from_predictions(preds_dict)

    if "errors" in result:
        return {"status": "failed", "errors": result["errors"]}

    return result


# ---------- HOME ----------
@app.get("/")
def home():
    return {
        "message": "Welcome to ChromaMatch API",
        "endpoints": {
            "/analyze": "Upload an image → ML analysis",
            "/recommend": "Send ML predictions → Get RAG recommendations",
            "/docs": "API docs",
        },
    }
