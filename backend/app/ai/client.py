import json
import time
import logging

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.client = genai.Client(api_key=self.api_key)

    def chat(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> dict:
        start = time.time()

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                    ),
                )
                elapsed = time.time() - start
                usage = response.usage_metadata
                return {
                    "content": response.text,
                    "tokens": {
                        "input": usage.prompt_token_count if usage else 0,
                        "output": usage.candidates_token_count if usage else 0,
                    },
                    "duration_seconds": round(elapsed, 2),
                }
            except Exception as e:
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    def chat_json(self, system_prompt: str, user_message: str, temperature: float = 0.2) -> dict:
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
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
