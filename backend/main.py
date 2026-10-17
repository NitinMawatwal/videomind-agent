from fastapi import FastAPI

app = FastAPI(title="VideoMind Agent")


@app.get("/health")
async def health_check():
    return {"status": "ok"}