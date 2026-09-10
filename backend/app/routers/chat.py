from fastapi import APIRouter

from app.schemas.chat import ChatRequest
from app.services import chat_service


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("/")
def chat(
    request: ChatRequest
):
    result = chat_service.ask_gpt(
        message=request.message,
        conversation_id=(
            request.conversation_id
        ),
    )

    return {
        "message": request.message,
        "answer": result["answer"],
        "conversation_id": (
            result["conversation_id"]
        ),
    }