"""
main.py
-------
FastAPI application entry point for Parchi backend.

Run with:
    uvicorn main:app --reload --port 8000

API docs available at:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from routes.health import router as health_router
from routes.stock import router as stock_router
from routes.ledgers import router as ledgers_router
from routes.challans import router as challans_router
from routes.auth import router as auth_router
from db.database import init_db

load_dotenv()

# Initialize Database
init_db()

app = FastAPI(
    title="Parchi",
    description="Delivery Challan Management & Inventory Optimization on top of TallyPrime",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — allow React dev server (port 5173) and local production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternate dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(stock_router, prefix="/api", tags=["Stock"])
app.include_router(ledgers_router, prefix="/api", tags=["Ledgers"])
app.include_router(challans_router, prefix="/api", tags=["Challans"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])


@app.get("/")
def root():
    return {
        "app": "Parchi",
        "version": "0.1.0",
        "phase": "Phase 1 — Proof of Concept",
        "docs": "/docs",
        "status": "running",
    }
