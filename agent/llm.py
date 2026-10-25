# agent/llm.py
"""Power layer: Meterless Nightshift (OpenAI-compatible) client routed to NVIDIA Nemotron."""
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

APP_HEADERS = {"meterless-app": "cyber-claims-explainer", "meterless-scope": "user"}


def _base_url() -> str:
    return (os.environ.get("METERLESS_BASE_URL") or os.environ["MODEL_BASE_URL"]).rstrip("/")


def _token() -> str:
    return os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ["MODEL_API_KEY"]


def llm_configured() -> bool:
    """True only if a real runtime token is present (not the .env.example placeholder)."""
    tok = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ.get("MODEL_API_KEY") or ""
    return bool(tok) and not tok.startswith("your-")


def get_meterless_client() -> OpenAI:
    """OpenAI-compatible client routed through Meterless Nightshift Runtime."""
    return OpenAI(base_url=_base_url(), api_key=_token(), default_headers=APP_HEADERS, timeout=30)


def discover_models() -> list:
    """GET /v1/models discovery required by the Meterless Runtime contract."""
    resp = requests.get(
        f"{_base_url()}/models",
        headers={"Authorization": f"Bearer {_token()}", **APP_HEADERS},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def call_nemotron(system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
    """Call NVIDIA Nemotron through Meterless Nightshift."""
    client = get_meterless_client()
    model_id = os.environ.get("NEMOTRON_MODEL") or os.environ.get("METERLESS_MODEL", "meterless/auto")
    response = client.chat.completions.create(
        model=model_id,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""
