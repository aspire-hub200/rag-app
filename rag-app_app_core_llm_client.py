import requests
from app.config import settings

def call_llm(system_prompt: str, user_prompt: str, model: str=None, max_tokens=512):
    url = settings.llm_api_url
    token = settings.openai_api_key
    if not url or not token:
        raise Exception("LLM API not configured")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "model": model or settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0
    }
    r = requests.post(url, json=body, headers=headers, timeout=60)
    r.raise_for_status()
    j = r.json()

    if "choices" in j and len(j["choices"])>0:
        return j["choices"][0]["message"]["content"]
    return j
