from fastapi import APIRouter

router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.get("/test")
def test_conversation_router():
    return {
        "message": "Conversation router is working"
    }