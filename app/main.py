from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Query
from pydantic import AnyHttpUrl

app = FastAPI(title="ContentVIP Pro API", version="1.0.0")


@app.get("/")
def root():
    return {
        "service": "contentvippro",
        "health": "/health",
        "docs": "/docs",
        "usage": "/api?url=https://example.com&views=2500",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api")
def create_campaign(
    url: AnyHttpUrl = Query(..., description="Target URL"),
    views: int = Query(0, ge=0, le=500_000, description="Internal target value"),
):
    return {
        "status": "queued",
        "job_id": str(uuid4()),
        "url": str(url),
        "views": views,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "message": (
            "Accepted for legitimate internal campaign processing. "
            "No fake views or automated engagement is generated."
        ),
    }
