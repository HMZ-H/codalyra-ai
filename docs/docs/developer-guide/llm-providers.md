---
sidebar_position: 4
title: LLM Providers
---

# LLM Provider System

Codalyra supports Gemini, OpenAI, and Anthropic through a pluggable provider abstraction.

## Provider Abstraction

All providers implement the `LLMProvider` abstract base class:

```python
class LLMProvider(ABC):
    @abstractmethod
    def chat_json(self, system_prompt: str, user_message: str, 
                  temperature: float = 0.2) -> dict:
        pass
```

The critical contract: `chat_json()` must return a **parsed Python dict**. Every downstream component (analyzer, scorer, report builder) depends on consistent structured output.

## JSON Output Strategies

Each provider uses a different mechanism for structured output:

### Gemini

```python
response = self.client.models.generate_content(
    model=self.model,
    contents=[...],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",  # Native JSON mode
        temperature=temperature,
    ),
)
return json.loads(response.text)
```

### OpenAI

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=[...],
    response_format={"type": "json_object"},  # Structured output
    temperature=temperature,
)
return json.loads(response.choices[0].message.content)
```

### Anthropic

Anthropic has no native JSON mode. The workaround: define a "tool" whose input schema matches the desired JSON structure, then force the model to call it:

```python
response = self.client.messages.create(
    model=self.model,
    system=system_prompt,
    messages=[{"role": "user", "content": user_message}],
    tools=[{
        "name": "review_output",
        "input_schema": {"type": "object", ...}
    }],
    tool_choice={"type": "tool", "name": "review_output"},
)
# Pre-parsed — no json.loads() needed
return tool_block.input
```

## Retry Logic

All providers retry up to 3 times with exponential backoff on:

- JSON parse failures
- API rate limit errors
- Transient network errors

If all retries fail, the agent returns empty findings rather than crashing.

## Provider Factory

```python
def create_provider(name: str, api_key: str, model: str = None) -> LLMProvider:
    if name == "gemini":
        return GeminiProvider(api_key, model or "gemini-3.6-flash")
    elif name == "openai":
        return OpenAIProvider(api_key, model or "gpt-4o-mini")
    elif name == "anthropic":
        return AnthropicProvider(api_key, model or "claude-sonnet-4")
```

## Provider Resolution Chain

When a Celery worker runs an agent, it resolves the provider in order:

1. Check `AgentConfig` for this project + agent type → specific provider
2. Get the user's encrypted API key for that provider → decrypt
3. If no config exists, fall back to the user's Gemini key
4. If no key at all → fail with a clear error message

## Available Models

```python
PROVIDER_MODELS = {
    "gemini": {
        "default": "gemini-3.6-flash",
        "models": ["gemini-3.6-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
    },
    "openai": {
        "default": "gpt-4o-mini",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o3-mini"],
    },
    "anthropic": {
        "default": "claude-sonnet-4-20250514",
        "models": ["claude-opus-4-20250514", "claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"],
    },
}
```

## Adding a New Provider

1. Create a new class extending `LLMProvider`
2. Implement `chat_json()` with the provider's JSON output mechanism
3. Add retry logic for transient failures
4. Register in `create_provider()` factory
5. Add to `PROVIDER_MODELS` dict
6. Update the frontend settings page to show the new provider option
