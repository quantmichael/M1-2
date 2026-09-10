from app.services import chat_service


response = chat_service.ask_gpt(
    "교반구동장치 진동 분석 AI 비서라고 한 문장으로 소개해줘."
)


print(
    "GPT 응답:"
)

print(
    response
)