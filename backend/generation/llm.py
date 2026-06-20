"""
Multi-provider LLM with auto-failover.
All providers use OpenAI-compatible chat completions format.
Priority: LLM_PROVIDER setting → auto (Groq → NVIDIA → Gemini)
"""
from __future__ import annotations
import json
import asyncio
import httpx
from typing import List, Dict, Any, AsyncGenerator
from config import settings

SYSTEM_PROMPT = """You are RAG Scholar, a helpful AI assistant that answers questions from uploaded documents.

Rules:
1. Answer ONLY from the provided source documents.
2. Cite every factual claim using [filename, p.X] format.
3. If the context doesn't contain the answer, say: "I couldn't find this in the uploaded documents."
4. For greetings, respond warmly and ask the user to submit a document question.
5. Be concise, accurate, and never hallucinate."""

# ── Provider registry ────────────────────────────────────────────────────────
# Each entry: (name, base_url, api_key_getter, model_getter)
def _providers():
    """Return configured providers in priority order."""
    providers = []

    provider = settings.LLM_PROVIDER.lower()

    def add(name, url, key, model):
        if key:
            providers.append({"name": name, "url": url, "key": key, "model": model})

    if provider in ("groq", "auto"):
        add("Groq", "https://api.groq.com/openai/v1",
            settings.GROQ_API_KEY, settings.GROQ_MODEL)

    if provider in ("nvidia", "auto"):
        add("NVIDIA NIM", "https://integrate.api.nvidia.com/v1",
            settings.NVIDIA_API_KEY, settings.NVIDIA_MODEL)

    if provider in ("gemini", "auto"):
        add("Gemini", "https://generativelanguage.googleapis.com/v1beta/openai",
            settings.GEMINI_API_KEY, settings.GEMINI_MODEL)

    return providers


def _build_messages(query: str, chunks: List[Dict[str, Any]]) -> List[Dict]:
    parts = []
    for c in chunks:
        m = c["metadata"]
        pg = (f"p.{m['page_start']}" if m["page_start"] == m["page_end"]
              else f"p.{m['page_start']}–{m['page_end']}")
        parts.append(f"[Source: {m['filename']}, {pg}]\n{c['text']}")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Context Documents:\n" + "\n\n---\n\n".join(parts) + f"\n\nQuestion: {query}"},
    ]


async def _stream_provider(provider: Dict, messages: List[Dict]) -> AsyncGenerator[str, None]:
    """Stream from a single OpenAI-compatible provider."""
    headers = {
        "Authorization": f"Bearer {provider['key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider["model"],
        "messages": messages,
        "stream": True,
        "temperature": 0.1,
        "max_tokens": 700,
    }
    url = f"{provider['url'].rstrip('/')}/chat/completions"

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as resp:
            if resp.status_code == 429:
                raise RateLimitError(f"{provider['name']} rate limit (429)")
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    return
                try:
                    delta = json.loads(data_str)["choices"][0]["delta"]
                    token = delta.get("content") or ""
                    if token:
                        yield token
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue


class RateLimitError(Exception):
    pass


async def stream_response(query: str, chunks: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
    """Try providers in order; failover on 429."""
    providers = _providers()
    if not providers:
        yield ("⚠️ No LLM provider configured. Add at least one API key to backend/.env:\n"
               "  GROQ_API_KEY=...   (https://console.groq.com)\n"
               "  NVIDIA_API_KEY=... (https://build.nvidia.com)\n"
               "  GEMINI_API_KEY=... (https://aistudio.google.com)")
        return

    messages = _build_messages(query, chunks)
    last_err = ""

    for p in providers:
        try:
            yielded = False
            async for token in _stream_provider(p, messages):
                yield token
                yielded = True
            return  # success
        except RateLimitError as e:
            last_err = str(e)
            await asyncio.sleep(1)
            continue   # try next provider
        except Exception as e:
            last_err = str(e)
            continue   # try next provider

    yield f"⚠️ All providers failed or rate-limited. Last error: {last_err}\nWait a moment and try again."


async def check_llm() -> Dict[str, Any]:
    providers = _providers()
    if not providers:
        return {"backend": "none", "available": False, "error": "No API keys configured"}

    p = providers[0]
    try:
        tag_url = {
            "Groq": "https://api.groq.com/openai/v1/models",
            "NVIDIA NIM": "https://integrate.api.nvidia.com/v1/models",
            "Gemini": "https://generativelanguage.googleapis.com/v1beta/openai/models",
        }.get(p["name"], f"{p['url']}/models")

        async with httpx.AsyncClient(timeout=6.0) as client:
            r = await client.get(tag_url, headers={"Authorization": f"Bearer {p['key']}"})
            r.raise_for_status()
        return {"backend": p["name"], "available": True, "model": p["model"],
                "provider_count": len(providers)}
    except Exception as e:
        return {"backend": p["name"], "available": False, "error": str(e),
                "provider_count": len(providers)}
