from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import os

app = FastAPI(
    title="Snake Scores API",
    description="Optional backend for submitting and retrieving Snake game scores.",
    version="1.0.0",
    openapi_tags=[{"name": "scores", "description": "Score submission and retrieval"}],
)

# Allow local dev and any configured frontend origin
frontend_url = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
origins = [frontend_url, "http://localhost:3000", "https://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
SCORES: List[dict] = []


class ScoreIn(BaseModel):
    name: str = Field(..., description="Player name", min_length=1, max_length=32)
    score: int = Field(..., description="Player score", ge=0)


class ScoreOut(BaseModel):
    name: str = Field(..., description="Player name")
    score: int = Field(..., description="Player score")


# PUBLIC_INTERFACE
@app.get("/health", tags=["health"])
def health():
    """Simple health endpoint."""
    return {"status": "ok"}


# PUBLIC_INTERFACE
@app.get(
    "/scores",
    response_model=dict,
    tags=["scores"],
    summary="Get scores",
    description="Retrieve a list of submitted scores sorted by highest score first.",
)
def get_scores():
    """Return top scores sorted descending."""
    top = sorted(SCORES, key=lambda s: s["score"], reverse=True)[:20]
    return {"scores": top}


# PUBLIC_INTERFACE
@app.post(
    "/scores",
    response_model=ScoreOut,
    tags=["scores"],
    summary="Submit score",
    description="Submit a player's score.",
)
def post_score(score: ScoreIn):
    """Submit a score and return the stored record."""
    rec = {"name": score.name.strip() or "Player", "score": int(score.score)}
    SCORES.append(rec)
    return rec


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "3001"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
