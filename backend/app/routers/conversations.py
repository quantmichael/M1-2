from fastapi import APIRouter

from app.schemas.conversation import ConversationCreate
from app.services import conversation_service


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


# --------------------------------------------------
# 대화 저장
# POST /api/conversations/
# --------------------------------------------------
@router.post("/")
def create_conversation(
    conversation: ConversationCreate
):
    return (
        conversation_service
        .create_conversation(conversation)
    )


# --------------------------------------------------
# 대화 목록 조회
# GET /api/conversations/
# --------------------------------------------------
@router.get("/")
def get_conversations():
    return (
        conversation_service
        .get_conversations()
    )


# --------------------------------------------------
# 특정 대화 조회
# GET /api/conversations/{id}
# --------------------------------------------------
@router.get("/{id}")
def get_conversation(id: str):
    return (
        conversation_service
        .get_conversation(id)
    )


# --------------------------------------------------
# 대화 삭제
# DELETE /api/conversations/{id}
# --------------------------------------------------
@router.delete("/{id}")
def delete_conversation(id: str):
    return (
        conversation_service
        .delete_conversation(id)
    )