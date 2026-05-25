import requests
from app.config.settings import settings


def call_ollama(prompt: str, max_tokens: int = 1000) -> str:
    """
    Send a prompt to locally running Ollama instance.
    Returns the response text.
    No API key needed — runs fully on your machine.
    """

    url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model" : settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,        # get full response at once
        "options": {
            "temperature"  : 0.4,
            "num_predict"  : max_tokens,
        }
    }

    try:
        response = requests.post(
            url,
            json   = payload,
            timeout= 120        # Ollama can be slow on first run
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        return (
            "Error: Cannot connect to Ollama. "
            "Make sure Ollama is running: 'ollama serve'"
        )
    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out. Try a smaller model."
    except Exception as e:
        return f"Error: {str(e)}"


def check_ollama_health() -> dict:
    """Check if Ollama is running and which models are available."""
    try:
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        data   = response.json()
        models = [m["name"] for m in data.get("models", [])]
        return {
            "status": "running",
            "models": models,
        }
    except Exception:
        return {
            "status": "offline",
            "models": [],
        }