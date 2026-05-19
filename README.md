<div align="center">

# 🤖 AI-Agent-Local-Infrastructure

### Local AI Agent Infrastructure — Persistent Memory · DingTalk Integration · Automated Task Scheduling

[![Status](https://img.shields.io/badge/Status-Production%20Ready-34d399?style=flat-square)]()
[![Platform](https://img.shields.io/badge/Platform-WSL%20%7C%20Linux-22d3ee?style=flat-square)]()
[![Agent](https://img.shields.io/badge/Agent-Hermes%20Agent-22c55e?style=flat-square)]()
[![GPU](https://img.shields.io/badge/GPU-NVIDIA%20RTX%204070%20Super-76B900?style=flat-square&logo=nvidia)]()
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**Designed &amp; Deployed by [TEAR5951](https://github.com/TEAR5951)**

[Architecture](#-architecture-overview) ·
[Features](#-core-features) ·
[Tech Stack](#-technology-stack) ·
[Quick Start](#-quick-start) ·
[Configuration](#-configuration) ·
[Projects](#-related-projects)

</div>

---

## 📋 Overview

**AI-Agent-Local-Infrastructure** is a fully deployed, production-grade local AI agent system that runs entirely on personal hardware. The infrastructure integrates:

- **Persistent Memory System** — Cross-session recall of user preferences, facts, and conversation context
- **Multi-Platform Messaging** — Real-time interaction via DingTalk (primary), CLI/TUI, and Telegram
- **Automated Task Scheduling** — Cron-based job engine for daily reminders, service health checks, and recurring tasks
- **Local Vision AI** — On-device image understanding with Qwen2.5-VL-7B at 4-bit quantization
- **Private LLM Gateway** — Local model inference accessible from all devices on the LAN
- **SubAgent Delegation** — Parallel task execution with isolated environments

> 🏠 **100% Private.** All data stays on your local machine. No data leaves the WSL/GPU boundary.

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                  LOCAL ENVIRONMENT (WSL + RTX 4070S)                 │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ DingTalk │  │   CLI    │  │ Telegram │  │  +More   │  ◀── ACCESS │
│  │   Chat   │  │  / TUI   │  │   Bot    │  │Platforms │     LAYER   │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│        │            │             │              │                   │
│        └────────────┼─────────────┼──────────────┘                   │
│                     ▼             ▼                                  │
│  ┌─────────────────────────────────────────────────────┐            │
│  │              HERMES GATEWAY                           │  ◀── GATE │
│  │  Platform Adapters · Message Routing · Sessions      │     WAY   │
│  └───────────────────────┬─────────────────────────────┘            │
│                          │ Message                                  │
│                          ▼                                          │
│  ┌─────────────────────────────────────────────────────┐            │
│  │              AI AGENT (Conversation Loop)            │  ◀── CORE │
│  │  LLM Reasoning · Tool Orchestration · Context Mgt   │            │
│  ├──────────────┬──────────────┬───────────────────────┤            │
│  │  🔧 Tool    │  🔄 SubAgent │  📚 Skills            │            │
│  │  System     │  Delegation  │  System                │            │
│  └──────┬──────┴──────┬───────┴──────────┬────────────┘            │
│         │             │                   │                         │
│         ▼             ▼                   ▼                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐              │
│  │ Persistent│  │  Cron    │  │  Session Database    │  ◀── INFRA  │
│  │  Memory   │  │ Scheduler│  │  (SQLite + FTS5)     │     STRUCT. │
│  └──────────┘  └──────────┘  └──────────────────────┘              │
│         │             │                                             │
│         ▼             ▼                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐              │
│  │  Vision  │  │  Local   │  │  Cloud LLM Provider  │  ◀── AI     │
│  │  Server  │  │LLM Gate. │  │  (DeepSeek V4 Flash) │     SERV.   │
│  │ :8800    │  │ :1234    │  │                       │              │
│  └──────────┘  └──────────┘  └──────────────────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

> 📊 **Full interactive diagram:** Open [`docs/architecture.html`](docs/architecture.html) in your browser.

---

## ⭐ Core Features

### 🧠 Persistent Memory System

| Feature | Description |
|---------|-------------|
| Long-term Storage | Facts, preferences, and user details survive across sessions |
| User Profile | Dedicated profile store for user identity and behavioral patterns |
| Cross-Session Recall | Automatically surface relevant past information in new conversations |
| Semantic Search | FTS5-powered full-text search across all past sessions |

### 📱 Multi-Platform Messaging

| Platform | Role | Status |
|----------|------|--------|
| **DingTalk** | Primary channel — daily reminders, real-time chat, work-mode interaction | ✅ Active |
| **CLI / TUI** | Direct terminal access, development, system administration | ✅ Active |
| **Telegram** | Secondary bot channel | ✅ Configured |
| **More** | Slack, Discord, WhatsApp — extensible via gateway plugins | ⚙️ Available |

### ⏰ Automated Task Scheduling

| Job | Schedule | Description |
|-----|----------|-------------|
| Morning Break | 10:56 daily | Reminder notification |
| Lunch Time | 11:56 daily | Meal reminder |
| Wake-up | 13:28 daily | Afternoon rest end reminder |
| Afternoon Break | 14:56 daily | Break reminder |
| Dinner Time | 17:56 daily | Evening meal reminder |
| End of Work | 19:56 daily | Work end notification |
| Vision Server Health | Every 1 minute | Auto-restart on failure |

### 👁️ Local Vision AI

Deployed on the same machine via **Vision Server** (`:8800`):

- **Model:** Qwen2.5-VL-7B-Instruct (4-bit NF4 quantization)
- **VRAM:** ~5.9 GB (leaves 6.1 GB free on RTX 4070 Super 12GB)
- **Latency:** ~3-6 seconds per image
- **API:** RESTful `/analyze`, `/health`, `/stats` endpoints
- **Input:** URL, Base64, or local file path

### 🛠 Tool &amp; SubAgent System

| Component | Description |
|-----------|-------------|
| **Tools** | Terminal (shell), File I/O, Web Search, Code Execution, Vision Analysis |
| **SubAgents** | Up to 3 concurrent delegated tasks in isolated contexts |
| **Skills** | 30+ built-in skills, auto-discovered from skills directory |
| **Plugins** | Extensible plugin system for custom functionality |

---

## 🛸 Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Agent Framework** | [Hermes Agent](https://hermes-agent.nousresearch.com) | Latest |
| **LLM Provider** | DeepSeek V4 Flash | — |
| **Primary Inference** | Cloud API (DeepSeek) | 1M context |
| **Local Vision** | Qwen2.5-VL-7B-Instruct | 4-bit NF4 |
| **Vision Framework** | PyTorch + Transformers + Flask | CUDA 12.1 |
| **Local LLM** | LM Studio (OpenAI-compatible API) | :1234 |
| **Messaging** | DingTalk (Corp API) | Gateway Plugin |
| **Scheduling** | Hermes Cron Engine | Interval + Cron |
| **Memory** | SQLite (FTS5) | — |
| **Delegation** | Hermes SubAgent System | 3 concurrent |
| **OS** | WSL (Windows Subsystem for Linux) | Ubuntu Noble |
| **GPU** | NVIDIA GeForce RTX 4070 Super | 12GB VRAM |
| **CPU** | AMD Ryzen 5 9600X | — |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| GPU | NVIDIA, 8GB+ VRAM | RTX 4070 Super 12GB |
| OS | Linux / WSL2 | Ubuntu 22.04+ / WSL2 |
| CUDA | 11.8+ | 12.1 |
| Python | 3.10 | 3.12 |
| RAM | 16GB | 32GB |

### 1. Install Hermes Agent

```bash
# Clone and install
git clone https://github.com/TEAR5951/AI-Agent-Local-Infrastructure.git
cd AI-Agent-Local-Infrastructure

# Or install Hermes Agent directly:
pip install hermes-agent
# See: https://hermes-agent.nousresearch.com/docs
```

### 2. Configure

```bash
# Copy the example config and customize:
cp config/config.yaml.example config/config.yaml

# Add your API keys to .env:
echo "DEEPSEEK_API_KEY=sk-xxxx" >> .env

# Configure DingTalk (optional):
# Add DingTalk client_id and client_secret in the platforms section of config.yaml
```

### 3. Launch

```bash
# Start Hermes Agent in CLI mode:
hermes

# Or with the Terminal UI:
hermes --tui

# For DingTalk gateway:
hermes gateway
```

---

## ⚙️ Configuration

The system is configured through `config.yaml`. Key sections:

```yaml
# Model & Provider
model:
  default: deepseek-v4-flash
  provider: deepseek
  context_length: 1048576

# Memory System
memory:
  memory_enabled: true
  user_profile_enabled: true

# Task Scheduling
cron:
  wrap_response: true

# Vision Server (auxiliary)
auxiliary:
  vision:
    provider: custom
    model: Qwen2.5-VL-7B-4bit
    base_url: http://localhost:8800/v1

# DingTalk Platform
platforms:
  dingtalk:
    extra:
      client_id: "YOUR_CLIENT_ID"
      client_secret: "YOUR_CLIENT_SECRET"
```

> 🔒 **Security:** Never commit `config.yaml` or `.env` with real credentials. The provided `config/config.yaml.example` is a safe template.

---

## 📁 Project Structure

```
AI-Agent-Local-Infrastructure/
├── README.md                         # Project overview (this file)
├── LICENSE                           # MIT License
├── .gitignore                        # Ignored files
├── docker-compose.yml                # Vision Server container config
├── config/
│   └── config.yaml.example           # Safe configuration template
├── docs/
│   ├── architecture.html             # Interactive architecture diagram
│   └── tech-stack.md                 # Detailed technology breakdown
└── scripts/
    └── (example scripts)
```

---

## 🔗 Related Projects

| Project | Description | Links |
|---------|-------------|-------|
| **vision-server** | Local Vision AI API (Qwen2.5-VL-7B, 4-bit) | [GitHub](https://github.com/TEAR5951/vision-server) |
| **local-llm-gateway** | Local LLM inference gateway (LM Studio + LAN access) | [GitHub](https://github.com/TEAR5951/local-llm-gateway) |

---

## 📌 Roadmap

- [x] Core agent infrastructure deployment
- [x] Multi-platform messaging (DingTalk, CLI, Telegram)
- [x] Persistent memory system
- [x] Automated cron job scheduling
- [x] Local Vision AI integration
- [ ] Web dashboard UI
- [ ] Multi-GPU load balancing
- [ ] Mobile app companion
- [ ] RAG document ingestion pipeline

---

<div align="center">

**Built with ❤️ by [TEAR5951](https://github.com/TEAR5951)** · AI Deployment Engineer

⭐ Star this repo if you find it useful!

</div>
