# Backend: FastAPI Server for Church Commute Recommendations

## Overview
This backend provides a FastAPI service to calculate optimal church commute routes based on train timetables. Endpoint: `/gotochurch` (GET).

## Requirements
- Python 3.11+
- Dependencies: FastAPI, Uvicorn (install via `uv sync` or `pip install -r requirements.txt`)

## Local Setup & Run
1. Navigate: `cd backend`
2. Install deps: `uv sync` (or `pip install -r requirements.txt`)
3. Run server: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

API docs: http://localhost:8000/docs

## API Usage
- Basic: `GET /gotochurch` (uses current time)
- With time: `GET /gotochurch?now=HH:MM` (e.g., ?now=07:30)

Response: JSON with routes, next trains, and ranked recommendations.

## Deploy to Render
- Root Dir: `/backend/`
- Build Cmd: `uv sync --frozen && uv cache prune --ci`
- Start Cmd: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Instance: Free (Hobby)

Update Git → Auto-deploy. Test: `https://go-to-church-backend.onrender.com/gotochurch`
