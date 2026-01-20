import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.config import get_settings


class LLMService:
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> dict:
        """Generate a response from the LLM and parse as JSON."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return json.loads(content)

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_llm_service() -> LLMService:
    return LLMService()
