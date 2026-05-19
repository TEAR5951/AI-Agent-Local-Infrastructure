"""DingTalk webhook message handler.

Supports:
- Outgoing webhook (DingTalk pushes messages to us)
- Custom bot callback (sending messages back to DingTalk groups)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger("gateway.dingtalk")


class DingTalkBot:
    """DingTalk custom bot client for sending messages to groups."""

    def __init__(self, webhook_url: str = "", secret: str = ""):
        self.webhook_url = webhook_url
        self.secret = secret

    def _sign(self) -> tuple[str, str]:
        """Generate timestamp and signature for secured webhook."""
        timestamp = str(int(time.time() * 1000))
        if not self.secret:
            return timestamp, ""

        sign_string = f"{timestamp}\n{self.secret}"
        signature = hmac.new(
            self.secret.encode("utf-8"),
            sign_string.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        import base64

        encoded = base64.b64encode(signature).decode("utf-8")
        return timestamp, encoded

    async def send_text(
        self,
        content: str,
        at_mobiles: Optional[list[str]] = None,
        is_at_all: bool = False,
    ) -> dict[str, Any]:
        """Send a text message to the DingTalk group."""
        payload = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": is_at_all,
            },
        }
        return await self._post(payload)

    async def send_markdown(
        self,
        title: str,
        text: str,
        at_mobiles: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Send a markdown message."""
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"atMobiles": at_mobiles or []},
        }
        return await self._post(payload)

    async def send_action_card(
        self,
        title: str,
        text: str,
        btn_orientation: str = "1",
        buttons: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        """Send an interactive action card message."""
        payload = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btnOrientation": btn_orientation,
                "btns": buttons or [],
            },
        }
        return await self._post(payload)

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Post a message to the DingTalk webhook."""
        if not self.webhook_url:
            logger.warning("DingTalk webhook URL not configured")
            return {"errcode": -1, "errmsg": "webhook not configured"}

        url = self.webhook_url
        timestamp, signature = self._sign()
        if signature:
            url += f"&timestamp={timestamp}&sign={signature}"

        async with httpx.AsyncClient(timeout=httpx.Timeout(15)) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

        if result.get("errcode") != 0:
            logger.error("DingTalk API error: %s", result.get("errmsg"))
        else:
            logger.info("Message sent to DingTalk successfully")

        return result


def verify_webhook_signature(
    body: bytes,
    signature: str,
    secret: str,
    timestamp: str,
) -> bool:
    """Verify DingTalk outgoing webhook signature."""
    if not secret:
        return True  # Skip verification if no secret configured

    sign_string = f"{timestamp}\n{secret}"
    expected = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            sign_string.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    return hmac.compare_digest(expected, signature)
