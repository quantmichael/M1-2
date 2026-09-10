from fastapi import FastAPI

from app.routers import chat, conversations, data


app = FastAPI(
    title="Mixer Vibration Monitoring AI Agent",
    description="교반구동장치 진동 데이터를 분석하는 AI Agent API",
    version="1.0.0",
)


app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {
        "message": "Mixer Vibration Monitoring AI Agent API is running"
    }