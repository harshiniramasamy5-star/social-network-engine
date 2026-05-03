# Social Network Analytics Engine

A graph-powered backend system that models a social network using real DSA algorithms — built as a first-year CS student.

## Algorithms Used
- **BFS** — Friend suggestions (LinkedIn style)
- **Dijkstra** — Shortest connection path between users
- **Max Heap** — Top influencer ranking in O(n log k)
- **Union-Find** — Community detection with path compression
- **Dynamic Programming** — 5-factor feed ranking pipeline

## Tech Stack
Python · FastAPI · Pydantic · REST API · Uvicorn

## Run Locally
pip install fastapi uvicorn pydantic
uvicorn main:app --reload

Visit http://localhost:8000/docs to explore all endpoints.