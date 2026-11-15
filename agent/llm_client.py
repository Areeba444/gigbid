import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def get_node_model(node_name: str) -> str:
    # Model selection based on role: small/fast for classifiers/routing, large for writer/critic
    if node_name in ["scout", "analyst", "risk_assessor", "compliance", "verifier", "pricing"]:
        return "openai/gpt-oss-20b"
    return "qwen/qwen3.8-27b"

def call_llm(
    prompt: str,
    system_instruction: str = "You are an expert AI assistant. Always return valid JSON matching the requested schema.",
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 800
) -> str:
    selected_model = model or "qwen/qwen3.8-27b"
    api_key = os.getenv("GROQ_API_KEY", GROQ_API_KEY)
    
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "GigBid-Agent/1.0"
    }
    
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        # If model quota or error, fallback to gpt-oss-20b
        if selected_model != "openai/gpt-oss-20b":
            return call_llm(prompt, system_instruction, model="openai/gpt-oss-20b", temperature=temperature, max_tokens=max_tokens)
        raise RuntimeError(f"Groq API error {e.code}: {err_msg}")
    except Exception as e:
        raise RuntimeError(f"LLM request error: {e}")
