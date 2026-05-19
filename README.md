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

User > What tasks do I have today?

Agent > 🔍 Checking scheduled jobs...
  ✓ Vision server keepalive (every 1m)
  ✓ 6 recurring reminders configured

  All systems running normally.
```

### DingTalk Chat
```
┌─────────────────────────────────────┐
│  Hermes AI Agent                    │
├─────────────────────────────────────┤
│                                     │
│  Hey, what's my schedule today?     │
│  ──────────────────────────         │
│                                     │
│  Good afternoon! 💙                 │
│  You have 3 reminders scheduled     │
│  before the end of work today.      │
│  I'll notify you at each one.       │
│                                     │
│  Got it, thanks!                    │
│  ──────────────────────────         │
│                                     │
│  No problem, I've got you covered   │
│  💙                                 │
└─────────────────────────────────────┘
```

### Vision API Response
```json
{
  "success": true,
  "description": "An orange cat sitting on a wooden floor, sunlight streaming through the window...",
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

## Contact

- Email: 2712247951@qq.com

## Related Projects

- [vision-server](https://github.com/TEAR5951/vision-server) — Local Vision AI API
- [local-llm-gateway](https://github.com/TEAR5951/local-llm-gateway) — Local LLM inference gateway
