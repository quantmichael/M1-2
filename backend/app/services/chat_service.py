import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

from app.schemas.conversation import (
    ConversationCreate,
    Message,
)
from app.services import (
    conversation_service,
    data_service,
)


# --------------------------------------------------
# 프로젝트 루트 .env 로드
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


# --------------------------------------------------
# 환경변수
# --------------------------------------------------
api_key = os.getenv("CODYSSEY_API_KEY")

api_url = os.getenv(
    "CODYSSEY_API_URL",
    "https://copa.codyssey.kr/v1/chat/completions"
)

model = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini"
)


if not api_key:
    raise ValueError(
        "CODYSSEY_API_KEY가 설정되지 않았습니다."
    )


# --------------------------------------------------
# System Prompt 생성
# --------------------------------------------------
def build_system_prompt():

    summary = (
        data_service
        .get_data_summary()
    )

    summary_json = json.dumps(
        summary,
        ensure_ascii=False,
        indent=2
    )

    system_prompt = f"""
당신은 교반구동장치 진동 상태 분석 AI Agent입니다.

아래 Manufacturing Summary를 근거로
사용자의 질문에 답하세요.

[Manufacturing Summary]

{summary_json}


[응답 규칙]

1. RMS는 교반구동장치의 진동 수준을 나타내는 핵심 지표입니다.

2. rms.percentile_rank는 현재 RMS 값이 전체 데이터에서
어느 백분위 위치인지 의미합니다.

3. trend의 normalized_change_percent는
해당 시간 구간에서 RMS가 얼마나 변화했는지를
전체 평균 RMS를 기준으로 정규화한 값입니다.

4. trend의 change_percentile_rank는
현재 변화량이 과거 동일 시간 구간의 변화량과 비교해
어느 백분위 위치인지 의미합니다.

5. change_percentile_rank가 80이라면
과거 동일 시간 구간 변화량의 약 80%보다
현재 변화량이 크다는 의미입니다.
이를 '상위 80%'라고 표현하지 마세요.

6. peak_to_peak.percentile_rank는
현재 진동 범위가 전체 데이터에서
어느 백분위 위치인지 의미합니다.

7. percentile 값은
고장 확률이나 이상 발생 확률이 아닙니다.

8. 제공된 데이터만 근거로 설명하세요.

9. 장비의 고장 여부를 단정하지 마세요.

10. 고장 원인이나 부품 이상 원인을 추측하지 마세요.

11. 데이터만으로 확인할 수 없는 내용은
확인할 수 없다고 설명하세요.

12. 사용자가 질문한 내용과 관련된 지표를 중심으로
간결하고 이해하기 쉽게 답하세요.
"""

    return system_prompt


# --------------------------------------------------
# GPT 질문
# --------------------------------------------------
def ask_gpt(
    message: str,
    conversation_id: str | None = None
):

    system_prompt = build_system_prompt()

    previous_messages = []

    # --------------------------------------------------
    # 기존 대화 조회
    # --------------------------------------------------
    if conversation_id:

        conversation = (
            conversation_service
            .get_conversation(
                conversation_id
            )
        )

        previous_messages = (
            conversation.get(
                "messages",
                []
            )
        )


    # --------------------------------------------------
    # GPT에 전달할 메시지 구성
    # --------------------------------------------------
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        *previous_messages,
        {
            "role": "user",
            "content": message
        }
    ]


    # --------------------------------------------------
    # GPT API 호출
    # --------------------------------------------------
    try:
        response = requests.post(
            api_url,

            headers={
                "Authorization": (
                    f"Bearer {api_key}"
                )
            },

            json={
                "model": model,
                "messages": messages,
            },

            timeout=60,
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="GPT API 응답 시간이 초과되었습니다."
        )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="GPT API 연결에 실패했습니다."
        )


    # --------------------------------------------------
    # 응답 JSON 처리
    # --------------------------------------------------
    try:
        result = response.json()

        answer = (
            result["choices"][0]
            ["message"]
            ["content"]
        )

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError,
    ):
        raise HTTPException(
            status_code=502,
            detail="GPT API 응답 형식을 처리할 수 없습니다."
        )


    # --------------------------------------------------
    # 저장할 대화 메시지 구성
    # --------------------------------------------------
    updated_messages = [
        *previous_messages,

        {
            "role": "user",
            "content": message
        },

        {
            "role": "assistant",
            "content": answer
        },
    ]


    # --------------------------------------------------
    # 기존 대화 업데이트
    # --------------------------------------------------
    if conversation_id:

        conversation_service \
            .update_conversation_messages(
                conversation_id,
                updated_messages
            )

        saved_id = conversation_id


    # --------------------------------------------------
    # 새로운 대화 저장
    # --------------------------------------------------
    else:

        conversation = ConversationCreate(
            title=message[:30],

            messages=[
                Message(
                    role=item["role"],
                    content=item["content"]
                )
                for item in updated_messages
            ],
        )

        saved_conversation = (
            conversation_service
            .create_conversation(
                conversation
            )
        )

        saved_id = (
            saved_conversation["id"]
        )


    return {
        "answer": answer,
        "conversation_id": saved_id,
    }