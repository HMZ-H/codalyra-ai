---
slug: pluggable-llm-providers
title: Building a Pluggable LLM Provider System That Doesn't Leak Keys
authors: [hamza]
tags: [llm, architecture]
---

Supporting Gemini, OpenAI, and Anthropic without a leaky abstraction — and encrypting every API key at rest.

Codalyra started as a Gemini-only app. Then the question came: "Can I use GPT-4 for the security agent and Claude for quality?" Suddenly I needed a provider abstraction that works identically across three very different APIs.

<!--truncate-->

## The Requirements

1. Works identically across Gemini, OpenAI, and Anthropic despite different APIs
2. Stores API keys securely (encrypted at rest, decrypted only at call time)
3. Allows per-agent per-project configuration
4. Falls back gracefully when a key is missing

## The Provider Abstraction

Every LLM provider must return structured JSON. The entire downstream pipeline depends on a consistent finding schema:

```python
class LLMProvider(ABC):
    @abstractmethod
    def chat_json(self, system_prompt: str, user_message: str,
                  temperature: float = 0.2) -> dict:
        pass
```

Each provider implements this differently:

- **Gemini**: `response_mime_type="application/json"` — native JSON mode
- **OpenAI**: `response_format={"type": "json_object"}` — structured output
- **Anthropic**: No native JSON mode — uses a tool-use workaround

## The Anthropic Trick

This was the hardest part. Anthropic's API has no JSON output mode. The solution: define a "tool" whose input schema matches the JSON structure you want, then force the model to call it:

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
return tool_block.input  # Pre-parsed dict, no json.loads() needed
```

The tool's input IS the structured JSON. Anthropic pre-parses it, so you get a Python dict directly.

## The Encryption Layer

API keys are stored encrypted using Fernet symmetric encryption:

```python
def _get_fernet():
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def encrypt_value(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()
```

Keys are encrypted on save and only decrypted inside the Celery worker right before making the LLM call. The plaintext exists in memory for the duration of one API call, never longer.

## Provider Resolution

The worker resolves which provider to use in order:

1. Check `AgentConfig` for a per-project per-agent provider
2. Get the user's encrypted key for that provider, decrypt it
3. If no config exists, fall back to the user's Gemini key
4. If no key at all, fail with a clear error message

This chain lets users run GPT-4o for security analysis (thorough but expensive) and Gemini Flash for quality checks (fast and cheap) within the same review.

## Takeaway

The abstraction is tiny — one abstract method, three implementations — but the design decisions around it (encryption, per-agent config, fallback chain, the Anthropic workaround) took more thought than the entire AI prompt system.
