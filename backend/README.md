# Snake Scores Backend (FastAPI)

Optional backend service for the Snake game to submit and retrieve scores. This service is optional; the frontend works standalone and will gracefully handle backend being unavailable.

## Endpoints

- GET /api/health → {"status":"ok"}
- GET /api/scores?limit=10 → returns top N scores sorted by score desc
  - Response: [{"name":"Alice","score":42,"ts":"2024-01-01T00:00:00Z"}, ...]
- POST /api/scores → submit a score
  - Request: {"name":"Alice","score":42}
  - Response: {"name":"Alice","score":42,"ts":"2024-01-01T00:00:00Z"}

OpenAPI docs: http://localhost:3001/docs

## Run locally

1. Create a virtual environment and install requirements:
   pip install -r requirements.txt

2. Start the server on port 3001:
   uvicorn main:app --host 0.0.0.0 --port 3001

3. Open API docs:
   http://localhost:3001/docs

## CORS

CORS is enabled for typical dev origins:
- http://localhost:3000
- https://localhost:3000
- FRONTEND_ORIGIN env var if provided

## Storage

- In-memory only (no database).
- Scores are kept up to the last 100 submissions and pruned on insert.
- Top scores endpoint returns the highest scores (default top 10).

## Environment

- FRONTEND_ORIGIN (optional): CORS allowed origin for the frontend (default http://localhost:3000).

## Notes

- Default server port is 3001; can be overridden using PORT env var.
- Frontend may use REACT_APP_API_BASE; if backend is down, frontend should continue to function without errors.
