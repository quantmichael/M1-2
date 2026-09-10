import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


api_key = os.getenv(
    "OPENAI_API_KEY"
)

model = os.getenv(
    "OPENAI_MODEL"
)


if not api_key:
    raise ValueError(
        "OPENAI_API_KEY가 설정되지 않았습니다."
    )


if not model:
    raise ValueError(
        "OPENAI_MODEL이 설정되지 않았습니다."
    )


client = OpenAI(
    api_key=api_key
)


response = client.responses.create(
    model=model,
    input="한 문장으로 인사해줘."
)


print(
    "GPT 응답:"
)

print(
    response.output_text
)