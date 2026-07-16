# DeepSeek V4 Pro Setup for OpenCode

## Quick Start

### 1. Get NVIDIA API Key

1. Go to https://build.nvidia.com
2. Sign up / log in
3. Click "Get API Key"
4. Copy your key (starts with `nvapi-`)

### 2. Set Environment Variable

```bash
export NVIDIA_API_KEY="nvapi-your-key-here"
```

Or add to `~/.zshrc`:
```bash
echo 'export NVIDIA_API_KEY="nvapi-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Restart OpenCode

```bash
# Quit opencode and restart
opencode
```

## Model Variants

| Mode | Command | Best For |
|------|---------|----------|
| **Max** (default) | Ask complex questions | Coding, reasoning |
| **High** | Say "think carefully" | General tasks |
| **Non-think** | Say "quick answer" | Simple questions |

## Free Tier Limits

- **40 RPM** (requests per minute)
- **No cost** for API calls
- opencode handles rate limiting automatically

## Files

- `opencode.json` - opencode configuration
- `.env.example` - API key template
- `deepseek-v4-variants.md` - Model comparison
- `deepseek-v4-pro-vs-nemotron-3-ultra.md` - vs Nemotron

## Available Free Models (144 total)

See `nvidia-build-free-models.md` for the complete list of 144 free endpoint models.

### Top Free Models for Coding

| Model | Context | Output | Best For |
|-------|---------|--------|----------|
| `deepseek-v4-pro` | 1M | 384k | Best quality |
| `deepseek-v4-flash` | 1M | 384k | Fastest |
| `nemotron-3-super-120b-a12b` | 1M | 32k | Tool calling |
| `qwen3.5-397b-a17b` | 256k | - | Multimodal |
| `minimax-m2.7` | 128k | - | 230B, coding |
