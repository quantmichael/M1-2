from fastapi import APIRouter, HTTPException

from app.firebase import db
from app.schemas.data import DataCreate, DataUpdate
from app.services import data_service


router = APIRouter(
    prefix="/api/data",
    tags=["Data"],
)


# --------------------------------------------------
# 데이터 전체 조회
# GET /api/data/
# --------------------------------------------------
@router.get("/")
def get_data():

    docs = db.collection(
        "data"
    ).stream()

    result = []

    for doc in docs:

        item = doc.to_dict()
        item["id"] = doc.id

        result.append(
            item
        )

    return result


# --------------------------------------------------
# Manufacturing Summary 조회
# GET /api/data/summary
# --------------------------------------------------
@router.get("/summary")
def get_data_summary():

    return (
        data_service
        .get_data_summary()
    )


# --------------------------------------------------
# 데이터 추가
# POST /api/data/
# --------------------------------------------------
@router.post("/")
def create_data(
    data: DataCreate
):

    doc_ref = (
        db.collection("data")
        .document()
    )

    new_data = {

        "date": (
            data.date.isoformat()
        ),

        "value": (
            data.value
        ),

        "memo": (
            data.memo
        ),

        "peak_to_peak": (
            data.peak_to_peak
        ),

        "sample_count": (
            data.sample_count
        ),
    }

    doc_ref.set(
        new_data
    )

    return {
        "id": doc_ref.id,
        **new_data,
    }


# --------------------------------------------------
# 데이터 수정
# PUT /api/data/{id}
# --------------------------------------------------
@router.put("/{id}")
def update_data(
    id: str,
    data: DataUpdate
):

    doc_ref = (
        db.collection("data")
        .document(id)
    )

    doc = (
        doc_ref.get()
    )

    if not doc.exists:

        raise HTTPException(
            status_code=404,
            detail="데이터를 찾을 수 없습니다."
        )

    update_fields = (
        data.model_dump(
            exclude_none=True
        )
    )

    if "date" in update_fields:

        update_fields["date"] = (
            update_fields["date"]
            .isoformat()
        )

    doc_ref.update(
        update_fields
    )

    updated_doc = (
        doc_ref
        .get()
        .to_dict()
    )

    return {
        "id": id,
        **updated_doc,
    }


# --------------------------------------------------
# 데이터 삭제
# DELETE /api/data/{id}
# --------------------------------------------------
@router.delete("/{id}")
def delete_data(id: str):

    doc_ref = (
        db.collection("data")
        .document(id)
    )

    doc = (
        doc_ref.get()
    )

    if not doc.exists:

        raise HTTPException(
            status_code=404,
            detail="데이터를 찾을 수 없습니다."
        )

    doc_ref.delete()

    return {

        "message": (
            "데이터가 삭제되었습니다."
        ),

        "id": id,
    }