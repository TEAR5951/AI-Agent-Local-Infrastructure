"""Configuration management for the AI Agent Gateway."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    from pydantic import BaseModel, Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    BaseModel = object
    BaseSettings = object

    class Field:
        def __init__(self, *args, **kwargs): ...

    class SettingsConfigDict:
        def __init__(self, *args, **kwargs): ...


class LLMConfig(BaseModel if BaseSettings is not object else object):
    """Configuration for the local LLM connection."""
    base_url: str = Field(
        default="http://localhost:1234/v1",
        description="OpenAI-compatible API endpoint (LM Studio / vLLM)",
    )
    api_key: str = Field(default="lm-studio", description="API key for local inference")
    model: str = Field(default="", description="Model name override (empty = auto-detect)")
    max_tokens: int = Field(default=4096, ge=1, le=32768)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    timeout: int = Field(default=60, ge=5)


class DingTalkConfig(BaseModel if BaseSettings is not object else object):
    """DingTalk bot configuration."""
    webhook_url: str = Field(default="", description="DingTalk outgoing webhook URL")
    token: str = Field(default="", description="DingTalk bot token for signature")
    app_key: str = Field(default="", description="DingTalk app key (optional)")
    app_secret: str = Field(default="", description="DingTalk app secret (optional)")


class MemoryConfig(BaseModel if BaseSettings is not object else object):
    """Memory storage configuration."""
    backend: str = Field(default="sqlite", description="Memory backend: sqlite | json")
    db_path: str = Field(default="./data/memory.db", description="SQLite database path")
    max_history: int = Field(default=100, description="Max conversation turns to retain")


class SchedulerConfig(BaseModel if BaseSettings is not object else object):
    """Scheduler configuration."""
    enabled: bool = Field(default=True)
    check_interval: int = Field(default=30, ge=5, description="Poll interval in seconds")


class GatewayConfig(BaseModel if BaseSettings is not object else object):
    """Root configuration model."""
    model_config = SettingsConfigDict(env_prefix="GATEWAY_", env_file=".env", extra="ignore")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8801, ge=1024, le=65535)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    llm: LLMConfig = Field(default_factory=LLMConfig)
    dingtalk: DingTalkConfig = Field(default_factory=DingTalkConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "GatewayConfig":
        """Load config from YAML file with env var overrides."""
        import yaml

        p = Path(path)
        if not p.exists():
            return cls()

        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)
