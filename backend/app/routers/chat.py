from fastapi import APIRouter

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.get("/test")
def test_chat_router():
    return {
        "message": "Chat router is working"
    }