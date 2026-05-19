# AI-Agent-Local-Infrastructure

AI infrastructure for persistent local intelligence and multi-platform agent workflows.

## Features

- Local LLM inference
- Persistent memory system
- DingTalk messaging integration
- Vision reasoning server
- Automated task scheduling
- Cross-platform deployment (WSL)

## How it works

DingTalk receives user messages and forwards them to the local gateway.  
The gateway calls the local LLM, loads persistent memory, and returns responses through DingTalk.  
Vision tasks are routed to the local vision server when image reasoning is required.

## Architecture

```
  User
    │
    ▼
┌─────────────┐
│  DingTalk   │
│    Bot      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Gateway    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Local LLM  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Memory    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Vision Server│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Scheduler  │
└─────────────┘
```

## Tech Stack

- Python
- Flask
- LM Studio
- Qwen2.5-VL-7B
- DingTalk Bot
- WSL
- Cron
- RTX 4070 Super

## Screenshots

### Terminal CLI
```
$ hermes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🤖 Hermes Agent
  Model: deepseek-v4-flash · Context: 1M tokens
  Platform: dingtalk · Skills: 28 loaded
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User > 帮我看看今天有什么任务

Agent > 🔍 Checking cron jobs...
  ✓ 6 jobs found (1 active, 5 paused)
  
  好的，今天到下班前还有这些：
    14:58 下午抽烟提醒
    17:58 晚饭提醒
    19:58 下班提醒
```

### DingTalk Chat
```
┌─────────────────────────────────────┐
│  Hermes AI Agent                    │
├─────────────────────────────────────┤
│                                     │
│  你在吗？今天有什么安排    14:32     │
│  ──────────────────────────         │
│                                     │
│  旭研，下午好 💙           14:32     │
│  今天14:58要去抽烟放风了            │
│  17:58吃晚饭，19:58下班             │
│                                     │
│  好的 知道了              14:33     │
│  ──────────────────────────         │
│                                     │
│  嗯，到点我提醒你          14:33     │
│  安心工作，有我在 💙                │
└─────────────────────────────────────┘
```

### Vision API Response
```json
{
  "success": true,
  "description": "图中一只橘色的猫蹲坐在木质地板上，阳光从窗户洒进来，场景温馨...",
  "inference_time_seconds": 4.52,
  "total_tokens": 285,
  "tokens_per_second": 63.1,
  "model": "Qwen/Qwen2.5-VL-7B-Instruct"
}
```

## Project Structure

```
gateway/     — DingTalk messaging gateway configuration
vision/      — Local vision reasoning server (Qwen2.5-VL-7B)
memory/      — Persistent memory system
scheduler/   — Automated task scheduling (cron jobs)
README.md    — This file
```

## Related Projects

- [vision-server](https://github.com/TEAR5951/vision-server) — Local Vision AI API
- [local-llm-gateway](https://github.com/TEAR5951/local-llm-gateway) — Local LLM inference gateway
