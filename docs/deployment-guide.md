# Deployment Guide

## Environment Setup

### WSL2 Configuration

```bash
# Install WSL2 (from Windows PowerShell as Admin)
wsl --install -d Ubuntu

# Verify WSL2
wsl -l -v

# Set default to WSL2
wsl --set-default-version 2
```

### NVIDIA CUDA in WSL2

```bash
# Install CUDA on Windows (https://developer.nvidia.com/cuda-downloads)
# WSL2 automatically passes through GPU drivers

# Verify GPU access in WSL
nvidia-smi
# Should show RTX 4070 Super with CUDA version
```

### Hermes Agent Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Hermes Agent
pip install hermes-agent

# Verify
hermes --version
```

## DingTalk Integration Setup

1. Go to [DingTalk Open Platform](https://open.dingtalk.com)
2. Create a new application (corp/internal app)
3. Get **Client ID** and **Client Secret**
4. Configure in `config.yaml`:
```yaml
platforms:
  dingtalk:
    extra:
      client_id: "your_client_id"
      client_secret: "your_client_secret"
```

5. Start the gateway:
```bash
hermes gateway
```

## Cron Job Setup

Jobs are managed through the agent interface:

```bash
# List all jobs
/hermes cron list

# Create a new job
/hermes cron create --name "job-name" --schedule "56 10 * * 0-6"

# Pause/resume
/hermes cron pause <job-id>
/hermes cron resume <job-id>
```

## Vision Server Deployment

### Method 1: Docker (Recommended)

```bash
docker-compose up -d
curl http://localhost:8800/health
```

### Method 2: Direct Python

```bash
# Install dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Start server
python server.py
```

> See the [vision-server](https://github.com/TEAR5951/vision-server) project for full details.

## Local LLM Gateway

1. Install [LM Studio](https://lmstudio.ai/) on Windows
2. Download a model (e.g., openai/gpt-oss-20b)
3. In Settings → OpenAI API Server:
   - Enable API server
   - Set `networkInterface` to `0.0.0.0`
   - Port: `1234`
4. Verify:
```bash
curl http://192.168.x.x:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-oss-20b", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 50}'
```

## Verification Checklist

- [ ] Hermes Agent CLI starts without errors
- [ ] Gateway connects to DingTalk
- [ ] Cron jobs execute on schedule
- [ ] Vision Server responds on `:8800/health`
- [ ] Session history persists across restarts
- [ ] Memory recalls previously saved facts
