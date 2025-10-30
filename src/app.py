from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="ChromaMatch")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # placeholder: save file and return dummy response
    return {
        "skin_tone": "warm",
        "undertone": "neutral",
        "face_shape": "oval",
        "recommendation": "Gold jewelry and earth tones suit you best.",
    }
