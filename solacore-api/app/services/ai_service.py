import asyncio
import json
from typing import AsyncGenerator

import httpx
from app.config import get_settings


class AIService:
    def __init__(self):
        self.settings = get_settings()
        self.provider = (self.settings.llm_provider or "openai").lower()
        self.timeout = httpx.Timeout(self.settings.llm_timeout)
        self.max_retries = 3

    def _get_stream_generator(
        self, system_prompt: str, user_prompt: str
    ) -> AsyncGenerator[str, None]:
        """Return the appropriate stream generator based on provider."""
        if self.provider == "openai":
            return self._stream_openai(system_prompt, user_prompt)
        elif self.provider == "anthropic":
            return self._stream_anthropic(system_prompt, user_prompt)
        elif self.provider == "openrouter":
            return self._stream_openrouter(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def stream(
        self, system_prompt: str, user_prompt: str
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from the configured provider."""
        attempt = 0
        while attempt < self.max_retries:
            attempt += 1
            yielded_any = False
            try:
                async for token in self._get_stream_generator(
                    system_prompt, user_prompt
                ):
                    yielded_any = True
                    yield token
                return
            except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError):
                if attempt >= self.max_retries or yielded_any:
                    raise
                await asyncio.sleep(0.5 * attempt)

    async def _stream_openai(
        self, system_prompt: str, user_prompt: str
    ) -> AsyncGenerator[str, None]:
        api_key = self.settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
            "max_tokens": self.settings.llm_max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if data == "[DONE]":
                        break
                    try:
                        payload = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    delta = payload.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content

    def _should_collect_reasoning(self) -> bool:
        """判断是否应该收集 reasoning 内容"""
        return (
            self.settings.openrouter_reasoning_fallback
            and self.settings.enable_reasoning_output
        )

    async def _process_openrouter_stream(
        self, response: httpx.Response
    ) -> AsyncGenerator[tuple[str | None, str | None], None]:
        """处理 OpenRouter SSE 流，返回 (content, reasoning) 元组"""
        async for line in response.aiter_lines():
            if not line or not line.startswith("data:"):
                continue
            data = line[len("data:") :].strip()
            if data == "[DONE]":
                break
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue
            delta = payload.get("choices", [{}])[0].get("delta", {})
            yield delta.get("content"), delta.get("reasoning")

    async def _stream_openrouter(
        self, system_prompt: str, user_prompt: str
    ) -> AsyncGenerator[str, None]:
        api_key = self.settings.openrouter_api_key
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")

        base_url = self.settings.openrouter_base_url.rstrip("/")
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
            "max_tokens": self.settings.llm_max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if self.settings.openrouter_referer:
            headers["HTTP-Referer"] = self.settings.openrouter_referer
        if self.settings.openrouter_app_name:
            headers["X-Title"] = self.settings.openrouter_app_name

        collect_reasoning = self._should_collect_reasoning()
        reasoning_buffer: list[str] = []
        yielded_content = False

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for content, reasoning in self._process_openrouter_stream(
                    response
                ):
                    if content:
                        yielded_content = True
                        yield content
                    elif collect_reasoning and reasoning:
                        reasoning_buffer.append(reasoning)

        # Reasoning 兜底：仅在启用时使用
        if collect_reasoning and not yielded_content and reasoning_buffer:
            yield "".join(reasoning_buffer)

    async def _stream_anthropic(
        self, system_prompt: str, user_prompt: str
    ) -> AsyncGenerator[str, None]:
        api_key = self.settings.anthropic_api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")

        payload = {
            "model": self.settings.llm_model,
            "max_tokens": self.settings.llm_max_tokens,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if not data:
                        continue
                    try:
                        payload = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    if payload.get("type") == "content_block_delta":
                        delta = payload.get("delta", {})
                        text = delta.get("text")
                        if text:
                            yield text
