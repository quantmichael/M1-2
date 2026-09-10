from fastapi import APIRouter

router = APIRouter(
    prefix="/api/data",
    tags=["Data"],
)


@router.get("/test")
def test_data_router():
    return {
        "message": "Data router is working"
    }