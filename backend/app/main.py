import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    chat,
    conversations,
    data,
)


# --------------------------------------------------
# 환경변수 로드
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


# --------------------------------------------------
# FastAPI
# --------------------------------------------------
app = FastAPI(
    title="Mixer Vibration Monitoring AI Agent",
    description="교반구동장치 진동 데이터를 분석하는 AI Agent API",
    version="1.0.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500"
)

allowed_origins = [
    origin.strip()
    for origin in allowed_origins_env.split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Router
# --------------------------------------------------
app.include_router(
    data.router
)

app.include_router(
    conversations.router
)

app.include_router(
    chat.router
)


# --------------------------------------------------
# Root
# --------------------------------------------------
@app.get("/")
def root():
    return {
        "message":
        "Mixer Vibration Monitoring AI Agent API is running"
    }