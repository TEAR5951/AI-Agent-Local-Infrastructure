"""Vision analysis module — client for local vision inference server.

Connects to the Qwen2.5-VL vision server for image understanding.
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger("vision.client")

DEFAULT_VISION_URL = "http://localhost:8800/v1"


class VisionClient:
    """Client for local vision inference server."""

    def __init__(
        self,
        base_url: str = DEFAULT_VISION_URL,
        timeout: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def analyze_image(
        self,
        image_path: str = "",
        image_url: str = "",
        image_data: Optional[bytes] = None,
        prompt: str = "请详细描述这张图片的内容",
    ) -> dict[str, Any]:
        """Analyze an image with the vision model.

        Args:
            image_path: Local file path to the image.
            image_url: Remote URL of the image.
            image_data: Raw image bytes (base64-encoded internally).
            prompt: Question or instruction about the image.

        Returns:
            Dict with 'description' (str) and 'model' (str).
        """
        image_url_final = self._resolve_image(image_path, image_url, image_data)
        if not image_url_final:
            return {"error": "No image source provided"}

        payload = {
            "model": "qwen2.5-vl",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url_final}},
                    ],
                }
            ],
            "max_tokens": 1024,
        }

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            return {
                "description": content,
                "model": data.get("model", "qwen2.5-vl"),
                "usage": data.get("usage", {}),
            }
        except httpx.TimeoutException:
            logger.error("Vision request timed out after %ss", self.timeout)
            return {"error": f"Request timed out ({self.timeout}s)"}
        except Exception as e:
            logger.exception("Vision analysis failed")
            return {"error": str(e)}

    async def list_models(self) -> list[str]:
        """List available models on the vision server."""
        try:
            response = await self.client.get("/models")
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.warning("Failed to list vision models: %s", e)
            return []

    async def health(self) -> dict[str, Any]:
        """Check vision server health."""
        try:
            response = await self.client.get("/health")
            return response.json()
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    def _resolve_image(
        self,
        image_path: str = "",
        image_url: str = "",
        image_data: Optional[bytes] = None,
    ) -> str:
        """Resolve an image to a data URL or remote URL."""
        if image_url:
            return image_url

        if image_data:
            import imghdr

            fmt = imghdr.what(None, h=image_data) or "png"
            b64 = base64.b64encode(image_data).decode("utf-8")
            return f"data:image/{fmt};base64,{b64}"

        if image_path:
            p = Path(image_path)
            if not p.exists():
                logger.error("Image not found: %s", image_path)
                return ""
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            ext = p.suffix.lstrip(".") or "png"
            return f"data:image/{ext};base64,{b64}"

        return ""

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
