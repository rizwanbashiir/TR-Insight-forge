import os
import requests
from dotenv import load_dotenv
from pathlib import Path

from app.config.settings import settings

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


def call_grok(prompt: str, max_tokens: int = 1000) -> str:
    """
    Send prompt to Grok API and return the response text.
    Returns error message string if API call fails.
    """

    api_key = settings.GROK_API_KEY
    api_url = settings.GROK_API_URL

    if not api_key:
        return "Error: GROK_API_KEY not configured in .env"

    if not api_url:
        return "Error: GROK_API_URL not configured in .env"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type" : "application/json"
    }

    payload = {
        "model"      : settings.GROK_MODEL,
        "messages"   : [
            {
                "role"   : "system",
                "content": (
                    "You are a senior business intelligence advisor. "
                    "Give precise, data-driven recommendations based "
                    "only on the data provided. Be concise and practical."
                )
            },
            {
                "role"   : "user",
                "content": prompt
            }
        ],
        "temperature": 0.4,      # lower = more factual, less creative
        "max_tokens" : max_tokens,
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data    = response.json()
        content = (
            data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
        )
        return content

    except requests.exceptions.Timeout:
        return "Error: Grok API request timed out after 30 seconds."
    except requests.exceptions.HTTPError as e:
        return f"Error: Grok API returned {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def check_grok_health() -> dict:
    """Check if Grok API is reachable and key is valid."""
    api_key = settings.GROK_API_KEY
    api_url = settings.GROK_API_URL

    if not api_key or not api_url:
        return {"status": "offline", "message": "API Key or URL missing"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type" : "application/json"
    }
    
    # Send a tiny prompt to verify
    payload = {
        "model"      : settings.GROK_MODEL,
        "messages"   : [{"role": "user", "content": "ping"}],
        "max_tokens" : 5
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return {"status": "running", "models": [settings.GROK_MODEL]}
    except Exception as e:
        return {"status": "offline", "message": str(e), "models": []}