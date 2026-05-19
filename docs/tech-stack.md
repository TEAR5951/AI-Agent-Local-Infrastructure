# Technology Stack — Detailed Breakdown

## Core Agent

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Agent Framework** | [Hermes Agent](https://hermes-agent.nousresearch.com) | AI agent conversation loop, tool orchestration, context management |
| **LLM Engine** | AIAgent class (`run_agent.py`) | Synchronous conversation loop with tool-calling, budget tracking, interrupt handling |
| **CLI** | `prompt_toolkit` + Rich | Interactive terminal with autocomplete, skins, history |

## Model Providers

| Provider | Model | Role | Context |
|----------|-------|------|---------|
| DeepSeek | V4 Flash | Primary LLM (reasoning, conversation) | 1,048,576 tokens |
| Custom (local) | Qwen2.5-VL-7B 4-bit | Vision analysis (auxiliary) | — |
| LM Studio | gpt-oss-20b (Q4_K_M) | Local fallback LLM | — |

## LLM Inference Layer

| Service | Port | Tech | Description |
|---------|------|------|-------------|
| **Vision Server** | `:8800` | Flask + PyTorch + Transformers | Qwen2.5-VL-7B with 4-bit NF4 quantization, REST API |
| **Local LLM Gateway** | `:1234` | LM Studio | OpenAI-compatible API, multi-model hot-swap |
| **Cloud API** | — | DeepSeek API | Primary inference provider, 1M context |

## Hardware

| Component | Spec | Role |
|-----------|------|------|
| **GPU** | NVIDIA RTX 4070 Super 12GB | Vision inference, LLM inference |
| **CPU** | AMD Ryzen 5 9600X | General compute |
| **Storage** | Colorful CN600 256GB | System and agent data |
| **Host OS** | Windows 11 | WSL2 host |
| **Agent OS** | WSL2 (Ubuntu Noble) | Agent runtime environment |

## Messaging Integration

| Platform | Protocol | Auth Method | Notes |
|----------|----------|-------------|-------|
| **DingTalk** | Corp API | Client ID + Secret | Primary channel, daily reminders |
| **Telegram** | Bot API | Bot Token | Secondary channel |
| **CLI/TUI** | Local | — | Direct access |

## Data Storage

| Store | Technology | Purpose |
|-------|-----------|---------|
| **Session DB** | SQLite + FTS5 | Conversation history with full-text search |
| **Memory** | JSON (in-memory + file) | Long-term fact storage, user profile |
| **Channel State** | JSON | Gateway connection state, platform routing |
| **Job Store** | JSON | Cron job definitions, schedule state |

## Scheduling

| Component | Type | Interval/Format |
|-----------|------|----------------|
| **Cron Engine** | Interval + Cron expression | `*/1 * * * *` — `0 10 * * 0-6` |
| **Job Executor** | Hermes Scheduler | Runs agent with self-contained prompts |
| **Vision Keepalive** | Watchdog | 1-minute interval health check + auto-restart |

## Development & Operations

| Area | Tooling |
|------|---------|
| **Version Control** | Git + GitHub |
| **Python** | 3.12 |
| **Containerization** | Docker + docker-compose (for Vision Server) |
| **Container Runtime** | NVIDIA Container Toolkit |
| **Monitoring** | Hermes logs (`agent.log`, `errors.log`, `gateway.log`) |
