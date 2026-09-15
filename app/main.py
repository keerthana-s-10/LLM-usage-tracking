from fastapi import FastAPI

app = FastAPI(title="LLM Usage Tracking API")


@app.get("/health")
def health():
    return {"status": "ok"}