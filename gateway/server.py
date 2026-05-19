"""AI Agent Gateway — FastAPI application.

Routes messages from DingTalk to local LLM inference,
with vision analysis, memory, and scheduling support.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, HTTPException

from .config import GatewayConfig
from .dingtalk import DingTalkBot
from .llm_client import LLMClient

logger = logging.getLogger("gateway.server")


class GatewayApp:
    """Main gateway application holding all components."""

    def __init__(self, config: GatewayConfig):
        self.config = config
        self.llm = LLMClient(
            base_url=config.llm.base_url,
            api_key=config.llm.api_key,
            model=config.llm.model,
            max_tokens=config.llm.max_tokens,
            temperature=config.llm.temperature,
            timeout=config.llm.timeout,
        )
        self.dingtalk = DingTalkBot(
            webhook_url=config.dingtalk.webhook_url,
            secret=config.dingtalk.token,
        )


# Global app state (set during lifespan)
app_state: dict[str, Any] = {"gateway": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    config = GatewayConfig.from_yaml()
    gateway = GatewayApp(config)
    app_state["gateway"] = gateway
    logger.info(
        "Gateway started on %s:%s | LLM: %s",
        config.host, config.port, config.llm.base_url,
    )
    yield
    await gateway.llm.close()
    logger.info("Gateway shut down")


app = FastAPI(
    title="AI Agent Local Gateway",
    description="Local AI infrastructure gateway — DingTalk → Local LLM",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint."""
    gateway: GatewayApp = app_state.get("gateway")
    if not gateway:
        raise HTTPException(503, "Gateway not initialized")

    llm_health = await gateway.llm.health()
    return {
        "status": "ok",
        "llm": llm_health,
        "version": "1.0.0",
    }


@app.get("/v1/models")
async def list_models() -> dict[str, Any]:
    """OpenAI-compatible model listing."""
    gateway: GatewayApp = app_state.get("gateway")
    if not gateway:
        raise HTTPException(503, "Gateway not initialized")

    return {
        "object": "list",
        "data": [
            {
                "id": gateway.llm.model,
                "object": "model",
                "created": 1700000000,
                "owned_by": "local",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> dict[str, Any]:
    """OpenAI-compatible chat completions (proxy to local LLM)."""
    gateway: GatewayApp = app_state.get("gateway")
    if not gateway:
        raise HTTPException(503, "Gateway not initialized")

    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", False)

    if stream:
        raise HTTPException(400, "Streaming not supported via REST proxy; use direct LLM endpoint")

    result = await gateway.llm.chat(
        messages=messages,
        max_tokens=body.get("max_tokens"),
        temperature=body.get("temperature"),
    )

    return {
        "id": "chatcmpl-local",
        "object": "chat.completion",
        "created": int(__import__("time").time()),
        "model": result.get("model", gateway.llm.model),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": result.get("role", "assistant"),
                    "content": result.get("content", ""),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": result.get("usage", {}),
    }


@app.post("/webhook/dingtalk")
async def dingtalk_webhook(request: Request) -> dict[str, Any]:
    """DingTalk outgoing webhook handler.

    Receives messages from DingTalk, processes with local LLM,
    and sends response back.
    """
    gateway: GatewayApp = app_state.get("gateway")
    if not gateway:
        raise HTTPException(503, "Gateway not initialized")

    body = await request.json()
    msg_type = body.get("msgtype", "")
    text_content = ""

    if msg_type == "text":
        text_content = body.get("text", {}).get("content", "").strip()
    elif msg_type == "markdown":
        text_content = body.get("markdown", {}).get("text", "").strip()

    if not text_content:
        return {
            "msgtype": "text",
            "text": {"content": "抱歉，我没看懂这条消息的内容 🤔"},
        }

    logger.info("Received DingTalk message: %s", text_content[:100])

    # Build conversation context
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个本地的 AI 助手，通过 DingTalk 接收消息。"
                "请用中文简洁自然地回答问题。"
                "不知道就说不知道，不要编造。"
            ),
        },
        {"role": "user", "content": text_content},
    ]

    try:
        result = await gateway.llm.chat(messages)
        reply = result.get("content", "抱歉，我现在无法回答这个问题。")

        # Optionally send back via DingTalk bot
        if gateway.dingtalk.webhook_url:
            await gateway.dingtalk.send_text(reply)

        return {
            "msgtype": "text",
            "text": {"content": reply},
        }
    except Exception as e:
        logger.exception("LLM call failed")
        return {
            "msgtype": "text",
            "text": {"content": f"抱歉，处理消息时出错了: {str(e)}"},
        }


@app.get("/")
async def root() -> dict[str, Any]:
    """API root info."""
    return {
        "service": "AI Agent Local Gateway",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "models": "GET /v1/models",
            "chat": "POST /v1/chat/completions",
            "dingtalk_webhook": "POST /webhook/dingtalk",
        },
    }


def main() -> None:
    """Run the gateway server."""
    config = GatewayConfig.from_yaml()

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    uvicorn.run(
        "gateway.server:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
