"""Low-level Groq / OpenAI-compatible transport client with robust JSON extraction."""

import json
from openai import OpenAI
from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

_client = OpenAI(api_key=LLM_API_KEY or "dummy", base_url=LLM_BASE_URL or "https://api.groq.com/openai/v1")


def call_llm(system: str, user: str, temperature: float = 0.2, max_tokens: int = 3000, json_mode: bool = True) -> dict | str:
    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY not configured")
    
    kwargs = {
        "model": LLM_MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = _client.chat.completions.create(**kwargs)
    content = resp.choices[0].message.content
    if not content:
        # Reasoning models can spend the whole budget thinking; surface that clearly.
        raise ValueError(f"LLM returned empty content (finish_reason={resp.choices[0].finish_reason}); "
                         "try a larger max_tokens or a different LLM_MODEL")

    if json_mode:
        try:
            return json.loads(content)
        except Exception:
            if "```json" in content:
                sub = content.split("```json")[1].split("```")[0].strip()
                return json.loads(sub)
            raise ValueError(f"Failed to parse LLM JSON response: {content}")
    return content