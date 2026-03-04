from openai import AsyncOpenAI
from typing import AsyncGenerator
from __future__ import annotations

from app.core.config import settings

# client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class AIClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def complete(
        self,
        *,
        model: str,
        system: str,
        user: str,
        max_tokens: int = 1800,
        temperature: float = 0.6,
        frequency_penalty: float = 0.3,
        presence_penalty: float = 0.1,
    ) -> str:
        resp = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        return resp.choices[0].message.content or ""

    async def stream(
        self,
        *,
        model: str,
        system: str,
        user: str,
        max_tokens: int = 1800,
        temperature: float = 0.6,
        frequency_penalty: float = 0.3,
        presence_penalty: float = 0.1,
    ) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=True,
        )

        async for event in stream:
            delta = event.choices[0].delta
            if delta and getattr(delta, "content", None):
                yield delta.content
