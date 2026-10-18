"""Minimal, dependency-free client for Crusoe Managed Inference (OpenAI-compatible)."""

from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_URL = "https://api.inference.crusoecloud.com/v1"
DEFAULT_MODEL = "nvidia/Nemotron-3.5-Lightning-30B-A3B"
RETRY_STATUSES = {429, 500, 502, 503, 504}


class CrusoeError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"Crusoe API error {status}: {body[:500]}")
        self.status = status
        self.body = body


def load_api_key(env_path: Optional[Path] = None) -> str:
    """Return CRUSOE_API_KEY from the environment, falling back to a local .env file."""
    key = os.environ.get("CRUSOE_API_KEY")
    if key:
        return key
    path = env_path or Path(__file__).resolve().parent.parent / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line.startswith("CRUSOE_API_KEY="):
                # Strip quotes but never shell-expand: keys may contain '$'.
                key = line.split("=", 1)[1].strip().strip("'\"")
                if key:
                    return key
    raise RuntimeError("CRUSOE_API_KEY not found in environment or .env")


class CrusoeClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = 120.0,
        max_retries: int = 5,
    ):
        self._api_key = api_key or load_api_key()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_status: Optional[int] = None
        self.last_headers: Dict[str, str] = {}

    def __repr__(self) -> str:
        return f"CrusoeClient(base_url={self.base_url!r}, model={self.model!r})"

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> Any:
        if method != 'GET' and os.environ.get('CORE_HQ_ALLOW_PAID_INFERENCE') != 'approved':
            raise RuntimeError('Paid inference disabled. Founder approval is required before setting CORE_HQ_ALLOW_PAID_INFERENCE=approved.')
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        for attempt in range(self.max_retries + 1):
            req = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    self.last_status = resp.status
                    self.last_headers = dict(resp.headers)
                    return json.load(resp)
            except urllib.error.HTTPError as e:
                self.last_status = e.code
                self.last_headers = dict(e.headers or {})
                body = e.read().decode(errors="replace")
                if e.code in RETRY_STATUSES and attempt < self.max_retries:
                    # Jittered exponential backoff per Crusoe's rate-limit guidance.
                    time.sleep(min(60.0, 2 ** attempt) + random.uniform(0, 0.5))
                    continue
                raise CrusoeError(e.code, body) from None

    def list_models(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/models")["data"]

    def chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """POST /chat/completions. Extra kwargs (tools, temperature, chat_template_kwargs, ...) pass through."""
        payload = {"model": model or self.model, "messages": messages, "max_tokens": max_tokens, **kwargs}
        return self._request("POST", "/chat/completions", payload)

    def ask(self, prompt: str, system: Optional[str] = None, **kwargs: Any) -> str:
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        resp = self.chat(messages, **kwargs)
        return resp["choices"][0]["message"].get("content") or ""
