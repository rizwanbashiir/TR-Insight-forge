import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend folder explicitly
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


def get_grok_recommendations(prompt):
    """
    Send prompt to Grok API
    """

    api_key = os.getenv("GROK_API_KEY")
    api_url = os.getenv("GROK_API_URL")

    # Debug check
    print("API KEY:", api_key)
    print("API URL:", api_url)

    if not api_key:
        return {
            "error": "GROK_API_KEY not found in .env"
        }

    if not api_url:
        return {
            "error": "GROK_API_URL not found in .env"
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }