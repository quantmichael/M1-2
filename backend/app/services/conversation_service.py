from datetime import datetime, timezone

from fastapi import HTTPException

from app.firebase import db
from app.schemas.conversation import ConversationCreate


# --------------------------------------------------
# 대화 저장
# --------------------------------------------------
def create_conversation(
    conversation: ConversationCreate
):
    doc_ref = (
        db.collection("conversations")
        .document()
    )

    new_conversation = {
        "title": conversation.title,

        "messages": [
            message.model_dump()
            for message in conversation.messages
        ],

        "created_at": (
            datetime.now(timezone.utc)
            .isoformat()
        ),
    }

    doc_ref.set(
        new_conversation
    )

    return {
        "id": doc_ref.id,
        **new_conversation,
    }


# --------------------------------------------------
# 대화 목록 조회
# --------------------------------------------------
def get_conversations():
    docs = (
        db.collection("conversations")
        .stream()
    )

    conversations = []

    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id

        conversations.append(
            item
        )

    conversations.sort(
        key=lambda x: x.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return conversations


# --------------------------------------------------
# 특정 대화 조회
# --------------------------------------------------
def get_conversation(id: str):
    doc_ref = (
        db.collection("conversations")
        .document(id)
    )

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="대화를 찾을 수 없습니다."
        )

    conversation = (
        doc.to_dict()
    )

    return {
        "id": doc.id,
        **conversation,
    }


# --------------------------------------------------
# 대화 삭제
# --------------------------------------------------
def delete_conversation(id: str):
    doc_ref = (
        db.collection("conversations")
        .document(id)
    )

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="대화를 찾을 수 없습니다."
        )

    doc_ref.delete()

    return {
        "message": "대화가 삭제되었습니다.",
        "id": id,
    }

def update_conversation_messages(
    id: str,
    messages: list
):
    doc_ref = (
        db.collection("conversations")
        .document(id)
    )

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="대화를 찾을 수 없습니다."
        )

    doc_ref.update({
        "messages": messages
    })

    return {
        "id": id,
        "messages": messages,
    }