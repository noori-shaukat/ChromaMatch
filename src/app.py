from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI(title="ChromaMatch")


class AnalyzeResponse(BaseModel):
    skin_tone: str
    undertone: str
    face_shape: str
    recommendation: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    # placeholder: save file and return dummy response
    return AnalyzeResponse(
        skin_tone="warm",
        undertone="neutral",
        face_shape="oval",
        recommendation="Gold jewelry and earth tones suit you best.",
    )


@app.get("/")
def home():
    return {
        "message": "Evidently Data Drift Dashboard available at /evidently",
        "docs": "/docs",
    }
