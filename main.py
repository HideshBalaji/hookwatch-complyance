from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/version")
async def version():
    return {
        "version":"1.0.0"
    }

