---
sidebar_position: 7
title: Settings
---

# Settings

Configure LLM providers, API keys, agent behavior, and notifications.

## LLM Provider Settings

Codalyra supports three LLM providers. Configure them under **Settings** → **API Keys**:

### Gemini (Default)

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `gemini-3.6-flash` | Fast | ~$0.002/review | Default, cost-effective |
| `gemini-2.5-pro` | Medium | ~$0.01/review | Higher accuracy |
| `gemini-2.0-flash` | Fast | ~$0.002/review | Alternative fast model |

### OpenAI

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `gpt-4o` | Medium | ~$0.02/review | Best accuracy |
| `gpt-4o-mini` | Fast | ~$0.003/review | Cost-effective |
| `o3-mini` | Medium | ~$0.01/review | Reasoning tasks |

### Anthropic

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `claude-sonnet-4` | Medium | ~$0.015/review | Balanced |
| `claude-opus-4` | Slow | ~$0.05/review | Best nuanced analysis |
| `claude-haiku-4.5` | Fast | ~$0.003/review | Cost-effective |

## API Key Storage

API keys are encrypted at rest using **Fernet symmetric encryption** (AES-128-CBC + HMAC-SHA256). Keys are:

- Encrypted when you save them via the UI
- Stored as ciphertext in the database
- Decrypted only inside Celery workers at LLM call time
- Never exposed in API responses

## Per-Agent Configuration

For each project, you can configure individual agents:

1. Go to your project → **Agent Config**
2. For each agent (Logic, Security, Performance, Quality):
   - **Enable/Disable** — Skip this agent entirely
   - **Provider** — Choose Gemini, OpenAI, or Anthropic
   - **Model** — Override the default model
   - **Custom Prompt** — Replace the system prompt

This lets you use different providers for different analysis types. For example, use Gemini Flash for quality checks (cheap, fast) and GPT-4o for security analysis (more thorough).

## Notification Settings

Configure where review results are sent:

- **Slack Webhook URL** — Posts Block Kit formatted messages
- **Discord Webhook URL** — Posts rich embed messages

These can be set globally (environment variables) or per-project.
