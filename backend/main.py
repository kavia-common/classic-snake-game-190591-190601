from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import os

# Create FastAPI app with OpenAPI metadata and tags
app = FastAPI(
    title="Snake Scores API",
    description="Optional backend for submitting and retrieving Snake game scores.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Service health endpoints"},
        {"name": "scores", "description": "Score submission and retrieval"},
    ],
)

# Configure CORS for local dev and optional explicit frontend origin
frontend_url = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
origins = list({frontend_url, "http://localhost:3000", "https://localhost:3000"})
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage and retention size
SCORES: List[dict] = []
MAX_SCORES = 100  # prune to last 100 entries


class ScoreIn(BaseModel):
    """Incoming score payload."""
    name: str = Field(..., description="Player name", min_length=1, max_length=32)
    score: int = Field(..., description="Player score", ge=0, le=1_000_000)


class ScoreOut(BaseModel):
    """Outgoing score payload."""
    name: str = Field(..., description="Player name")
    score: int = Field(..., description="Player score")
    ts: str = Field(..., description="ISO timestamp when the score was recorded")


# PUBLIC_INTERFACE
@app.get(
    "/api/health",
    tags=["health"],
    summary="Health check",
    description="Simple service health endpoint.",
)
def health():
    """Return service health status."""
    return {"status": "ok"}


# PUBLIC_INTERFACE
@app.get(
    "/api/scores",
    tags=["scores"],
    summary="Get top scores",
    description="Retrieve top N scores sorted by highest score first. Default top 10.",
    responses={
        200: {
            "description": "List of scores",
            "content": {
                "application/json": {
                    "example": [
                        {"name": "Alice", "score": 42, "ts": "2024-01-01T00:00:00Z"}
                    ]
                }
            },
        }
    },
)
def get_scores(limit: Optional[int] = 10):
    """Return top scores sorted descending by score."""
    try:
        n = int(limit or 10)
    except Exception:
        n = 10
    if n <= 0:
        n = 10
    # sort by score desc, then ts asc (older first if tie)
    top = sorted(
        SCORES,
        key=lambda s: (-int(s.get("score", 0)), s.get("ts", "")),
    )[: n if n > 0 else 10]
    return top


# PUBLIC_INTERFACE
@app.post(
    "/api/scores",
    tags=["scores"],
    summary="Submit a score",
    description="Submit a player's score. Returns the created entry.",
    response_model=ScoreOut,
    responses={
        201: {"description": "Score created"},
        422: {"description": "Validation error"},
    },
)
def post_score(score: ScoreIn):
    """Validate and store a score in memory, pruning to MAX_SCORES on insert."""
    # Normalize and validate name
    clean_name = score.name.strip()
    if not clean_name:
        raise HTTPException(status_code=422, detail="Name must not be empty")

    # Build record with ISO timestamp (UTC, Z-suffix)
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rec = {"name": clean_name, "score": int(score.score), "ts": ts}
    SCORES.append(rec)

    # prune to last MAX_SCORES by recency
    if len(SCORES) > MAX_SCORES:
        del SCORES[0 : len(SCORES) - MAX_SCORES]

    # Return 201 Created semantics (FastAPI returns 200 by default, acceptable for minimal API)
    return rec


if __name__ == "__main__":
    import uvicorn

    # Default to port 3001 for preview environments
    port = int(os.getenv("PORT", "3001"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
