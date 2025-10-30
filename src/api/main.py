from fastapi import FastAPI

app = FastAPI(title="ColorMatch")


@app.get("/health")
def health_check():
    return {"status": "ok"}
