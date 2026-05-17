from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database.db import engine, Base
import app.models.webhook  # Import models to register them with Base

Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="HookWatch API",
    description="Webhook Reliability & Replay Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "project":"HookWatch",
        "status":"running",
        "message":"Webhook Reliability Intelligence Platform"
    }

@app.get("/health")
async def health():
    return {
        "status":"healthy"
    }

@app.get("/test-db")
async def test_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "success",
            "message": "Successfully connected to the database!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/version")
async def version():
    return {
        "version":"1.0.0"
    }
