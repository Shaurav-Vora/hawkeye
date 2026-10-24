import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_meterless_client() -> OpenAI:
    """Returns an OpenAI-compatible client routed through Meterless Nightshift Runtime."""
    base_url = os.environ.get("METERLESS_BASE_URL") or os.environ.get("MODEL_BASE_URL", "http://127.0.0.1:8088/v1")
    token = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ.get("MODEL_API_KEY", "")

    return OpenAI(
        base_url=base_url,
        api_key=token,
        default_headers={
            "meterless-app": "cyber-claims-explainer",
            "meterless-scope": "user",
        },
    )

def discover_models() -> list:
    """Implements GET /v1/models discovery required by the Meterless Runtime contract."""
    base_url = (os.environ.get("METERLESS_BASE_URL") or os.environ.get("MODEL_BASE_URL", "http://127.0.0.1:8088/v1")).rstrip("/")
    token = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ.get("MODEL_API_KEY", "")
    
    resp = requests.get(
        f"{base_url}/models",
        headers={
            "Authorization": f"Bearer {token}",
            "meterless-app": "cyber-claims-explainer",
            "meterless-scope": "user",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])

def call_nemotron(system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
    """Calls NVIDIA Nemotron through Meterless Nightshift."""
    client = get_meterless_client()
    model_id = os.environ.get("NEMOTRON_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
    
    response = client.chat.completions.create(
        model=model_id,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # Quick sanity check
    print("Testing connection to Nightshift & Nemotron...")
    try:
        reply = call_nemotron(
            system_prompt="You are a helpful assistant.",
            user_prompt="Reply with the single word: READY"
        )
        print(f"Success! Model reply: {reply}")
    except Exception as e:
        print(f"Error testing connection: {e}")