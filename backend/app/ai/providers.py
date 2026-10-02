import json
import logging
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

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


class LLMProvider(ABC):
    @abstractmethod
    def chat_json(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> dict:
        pass


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        from google import genai
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def chat_json(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> dict:
        from google.genai import types
        start = time.time()

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                        response_mime_type="application/json",
                    ),
                )
                elapsed = time.time() - start
                usage = response.usage_metadata
                parsed = json.loads(response.text)
                return {
                    "data": parsed,
                    "tokens": {
                        "input": usage.prompt_token_count if usage else 0,
                        "output": usage.candidates_token_count if usage else 0,
                    },
                    "duration_seconds": round(elapsed, 2),
                }
            except json.JSONDecodeError:
                logger.warning(f"JSON parse failed on attempt {attempt + 1}")
                if attempt == 2:
                    return {
                        "data": {"findings": [], "summary": "Failed to parse LLM response."},
                        "tokens": {"input": 0, "output": 0},
                        "duration_seconds": round(time.time() - start, 2),
                    }
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        import openai
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def chat_json(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> dict:
        start = time.time()

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                elapsed = time.time() - start
                usage = response.usage
                parsed = json.loads(response.choices[0].message.content)
                return {
                    "data": parsed,
                    "tokens": {
                        "input": usage.prompt_tokens if usage else 0,
                        "output": usage.completion_tokens if usage else 0,
                    },
                    "duration_seconds": round(elapsed, 2),
                }
            except json.JSONDecodeError:
                logger.warning(f"JSON parse failed on attempt {attempt + 1}")
                if attempt == 2:
                    return {
                        "data": {"findings": [], "summary": "Failed to parse LLM response."},
                        "tokens": {"input": 0, "output": 0},
                        "duration_seconds": round(time.time() - start, 2),
                    }
                time.sleep(1)
            except Exception as e:
                logger.warning(f"OpenAI attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat_json(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> dict:
        start = time.time()

        json_instruction = "\n\nRespond with valid JSON only. No markdown, no explanation outside JSON."
        full_system = system_prompt + json_instruction

        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=full_system,
                    messages=[{"role": "user", "content": user_message}],
                    temperature=temperature,
                )
                elapsed = time.time() - start
                content = response.content[0].text
                parsed = json.loads(content)
                return {
                    "data": parsed,
                    "tokens": {
                        "input": response.usage.input_tokens,
                        "output": response.usage.output_tokens,
                    },
                    "duration_seconds": round(elapsed, 2),
                }
            except json.JSONDecodeError:
                logger.warning(f"JSON parse failed on attempt {attempt + 1}")
                if attempt == 2:
                    return {
                        "data": {"findings": [], "summary": "Failed to parse LLM response."},
                        "tokens": {"input": 0, "output": 0},
                        "duration_seconds": round(time.time() - start, 2),
                    }
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Anthropic attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)


def create_provider(provider_name: str, api_key: str, model: str | None = None) -> LLMProvider:
    providers = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    cls = providers.get(provider_name)
    if not cls:
        raise ValueError(f"Unknown provider: {provider_name}. Supported: {', '.join(providers)}")

    default_model = PROVIDER_MODELS[provider_name]["default"]
    return cls(api_key=api_key, model=model or default_model)
