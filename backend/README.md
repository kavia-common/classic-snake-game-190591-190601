# Snake Scores Backend (FastAPI)

Optional backend service for the Snake game to submit and retrieve scores.

## Run locally

1. Create a virtual environment and install requirements:
   pip install -r requirements.txt

2. Start the server on port 3001:
   uvicorn main:app --host 0.0.0.0 --port 3001

3. Open API docs:
   http://localhost:3001/docs

Environment:
- FRONTEND_ORIGIN (optional): CORS allowed origin for the frontend (default http://localhost:3000).
