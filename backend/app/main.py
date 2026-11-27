from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok"}