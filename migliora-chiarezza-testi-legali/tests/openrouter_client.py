#!/usr/bin/env python3
"""Client minimo OpenRouter (solo standard library) per i test dal vivo.

La chiave si legge da ~/.config/openrouter/key oppure dalla variabile
OPENROUTER_API_KEY e non viene mai stampata ne' salvata negli output.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"
KEY_PATH = Path.home() / ".config" / "openrouter" / "key"

# Provider fissati per rendere i run confrontabili (verificati il 2026-09-23 su
# /api/v1/models/<id>/endpoints). allow_fallbacks=False evita che OpenRouter
# cambi provider (e quantizzazione) a meta' benchmark. Il provider DeepSeek
# ufficiale risponde 404 con le impostazioni privacy dell'account: si usa
# DeepInfra in fp8.
PINNED_PROVIDERS = {
    "deepseek/deepseek-v4.1-flash": "deepinfra/fp8",
    "qwen/qwen3.8-flash": "alibaba",
}


def api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key and KEY_PATH.exists():
        key = KEY_PATH.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError("Chiave OpenRouter assente: ~/.config/openrouter/key o OPENROUTER_API_KEY.")
    return key


def _post(payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/avvocati-e-mac/skill-legali",
            "X-Title": "skill-legali chiarezza eval",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def chat(
    model: str,
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    temperature: float = 0.3,
    max_tokens: int = 16000,
    provider: str | None = None,
    response_format: dict[str, Any] | None = None,
    retries: int = 4,
    timeout: int = 300,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "usage": {"include": True},
    }
    pinned = provider or PINNED_PROVIDERS.get(model)
    if pinned:
        payload["provider"] = {"order": [pinned], "allow_fallbacks": False}
    if tools:
        payload["tools"] = tools
    if response_format:
        payload["response_format"] = response_format

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            data = _post(payload, timeout)
            if "error" in data:
                raise RuntimeError(json.dumps(data["error"])[:500])
            return data
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as error:
            last_error = error
            detail = ""
            if isinstance(error, urllib.error.HTTPError):
                try:
                    detail = error.read().decode("utf-8")[:300]
                except Exception:  # pragma: no cover - solo diagnostica
                    detail = ""
                if error.code in {400, 401, 402, 403, 404}:
                    raise RuntimeError(f"OpenRouter HTTP {error.code}: {detail}") from error
            time.sleep(2 ** attempt * 3)
    raise RuntimeError(f"OpenRouter non raggiungibile dopo {retries} tentativi: {last_error}")
