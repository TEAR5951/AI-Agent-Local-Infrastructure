"""OpenAI-compatible client for local LLM inference.

Connects to any OpenAI-compatible endpoint:
- LM Studio (http://localhost:1234)
- vLLM (http://localhost:8000)
- LocalAI (http://localhost:8080)
"""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Optional

import httpx

logger = logging.getLogger("gateway.llm")


class LLMClient:
    """Async client for local LLM inference."""

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        api_key: str = "lm-studio",
        model: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model or self._auto_detect_model()
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        return self._client

    def _auto_detect_model(self) -> str:
        """Auto-detect the loaded model name from the inference server."""
        try:
            import requests

            url = f"{self.base_url.replace('/v1', '')}/v1/models"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                if models:
                    name = models[0].get("id", "")
                    logger.info("Auto-detected model: %s", name)
                    return name
        except Exception as e:
            logger.warning("Model auto-detection failed: %s", e)

        logger.info("No model auto-detected, using default")
        return "local-model"

    async def chat(
        self,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | AsyncIterator[str]:
        """Send a chat completion request.

        Args:
            messages: OpenAI-format message list.
            stream: If True, returns an async iterator of delta strings.
            **kwargs: Override defaults (max_tokens, temperature, etc.).

        Returns:
            Full response dict (stream=False) or async iterator (stream=True).
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": stream,
        }

        if stream:
            return self._stream_chat(payload)

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        return {
            "role": "assistant",
            "content": data["choices"][0]["message"]["content"],
            "model": data.get("model", self.model),
            "usage": data.get("usage", {}),
        }

    async def _stream_chat(self, payload: dict[str, Any]) -> AsyncIterator[str]:
        """Stream chat completion response."""
        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                chunk = line[6:]
                if chunk.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    delta = data["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

    async def health(self) -> dict[str, Any]:
        """Check if the LLM server is reachable and healthy."""
        try:
            response = await self.client.get("/models")
            models = response.json().get("data", [])
            return {
                "status": "ok",
                "models_available": len(models),
                "models": [m["id"] for m in models[:5]],
            }
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
