from fastapi import FastAPI, UploadFile, File
from src.models.chroma_model import analyze_image
import tempfile
import shutil

app = FastAPI(title="ColorMatch")


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    result = analyze_image(temp_path)
    return result


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def home():
    return {
        "message": "Evidently Data Drift Dashboard available at /evidently",
        "docs": "/docs",
    }
