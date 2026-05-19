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
Vision requests are routed to the local vision server when image reasoning is required.

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

| Terminal CLI | DingTalk Chat | Vision API |
|:---:|:---:|:---:|
| ![terminal-cli](screenshots/terminal-cli.svg) | ![dingtalk-chat](screenshots/dingtalk-chat.svg) | ![vision-api](screenshots/vision-api.svg) |

DingTalk agent running locally with persistent memory, vision reasoning, and scheduled reminders.

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
