from app.firebase import db


doc_ref = db.collection("data").document("test")

doc_ref.set({
    "date": "2021-11-18T01:39:59.605Z",
    "value": 1.941249,
    "memo": "Firestore 연결 테스트"
})

print("저장 완료")


doc = doc_ref.get()

if doc.exists:
    print("조회 성공")
    print(doc.to_dict())
else:
    print("문서를 찾을 수 없습니다")