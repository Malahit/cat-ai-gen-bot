import asyncio
import base64
import logging
from typing import Optional

import aiohttp


API_URL = "https://api.perplexity.ai/chat/completions"


async def _fetch_placeholder_cat() -> Optional[bytes]:
    """Fallback cute cat when AI generation fails."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cataas.com/cat") as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception as exc:  # pragma: no cover - best effort fallback
        logging.warning("Placeholder cat fetch failed: %s", exc)
    return None


async def generate_cat_image(perplexity_key: str, prompt: str) -> Optional[bytes]:
    """
    Call Perplexity API to generate a vibrant cat image.

    The sonar-pro model is text-first; we request a base64 encoded PNG
    string and gracefully fall back to a placeholder cat if decoding fails.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {perplexity_key}",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI image generator. Return only a base64-encoded PNG "
                    "string without any surrounding text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate image of a cute realistic cat in {prompt}, vibrant colors, "
                    "detailed fur, 1024x1024. Return base64 PNG only."
                ),
            },
        ],
        "temperature": 0.3,
    }

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.post(API_URL, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    logging.error("Perplexity API error %s: %s", resp.status, await resp.text())
                    return await _fetch_placeholder_cat()
                data = await resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    return await _fetch_placeholder_cat()
                try:
                    return base64.b64decode(content, validate=True)
                except Exception:
                    logging.warning(
                        "Perplexity response was not base64 (model is text-first); using placeholder cat."
                    )
                    return await _fetch_placeholder_cat()
    except asyncio.TimeoutError:
        logging.error("Perplexity request timed out")
    except Exception as exc:  # pragma: no cover - network errors best effort
        logging.exception("Perplexity call failed: %s", exc)
    return await _fetch_placeholder_cat()
