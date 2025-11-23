# backend/main.py
"""
FastAPI app init. Includes routers and auto-create tables on startup.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routes.upload import router as invoice_router

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI(title="AI Invoice Extractor - Dawg Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(invoice_router)

@app.on_event("startup")
def on_startup():
    # Create database tables if not present
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "AI Invoice Extractor backend running."}
