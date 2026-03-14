import asyncio
import logging
import os
from typing import Optional

import aiohttp

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
FAL_API_URL = "https://fal.run/fal-ai/flux/schnell"


async def _fetch_placeholder_cat() -> Optional[bytes]:
    """Fallback cute cat when all generation fails."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cataas.com/cat") as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception as exc:
        logging.warning("Placeholder cat fetch failed: %s", exc)
    return None


async def _enhance_prompt(perplexity_key: str, user_prompt: str) -> str:
    """
    Use Perplexity sonar-pro to turn a short user prompt into a
    detailed Stable-Diffusion-style image prompt.
    Returns the enhanced prompt, or the original on any error.
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
                    "You are a prompt engineer for AI image generation. "
                    "Expand the user's short description into a single vivid, "
                    "detailed image generation prompt (max 120 words). "
                    "Always include: a cute realistic cat as the main subject, "
                    "photorealistic style, detailed fur, vibrant colors, 8k quality. "
                    "Return ONLY the prompt text, no explanations."
                ),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 180,
    }
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            async with session.post(
                PERPLEXITY_API_URL, json=payload, headers=headers
            ) as resp:
                if resp.status != 200:
                    logging.warning(
                        "Perplexity prompt enhancement failed %s", resp.status
                    )
                    return user_prompt
                data = await resp.json()
                enhanced = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                return enhanced if enhanced else user_prompt
    except Exception as exc:
        logging.warning("Prompt enhancement error: %s", exc)
        return user_prompt


async def _generate_with_fal(fal_key: str, prompt: str) -> Optional[bytes]:
    """
    Call fal.ai FLUX Schnell to generate an image.
    Returns raw image bytes or None on failure.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Key {fal_key}",
    }
    payload = {
        "prompt": prompt,
        "image_size": "square_hd",
        "num_inference_steps": 4,
        "num_images": 1,
        "enable_safety_checker": True,
    }
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                FAL_API_URL, json=payload, headers=headers
            ) as resp:
                if resp.status != 200:
                    logging.error(
                        "fal.ai error %s: %s", resp.status, await resp.text()
                    )
                    return None
                data = await resp.json()
                images = data.get("images", [])
                if not images:
                    logging.error("fal.ai returned no images: %s", data)
                    return None
                image_url = images[0].get("url")
                if not image_url:
                    return None
                # Download the generated image
                async with session.get(image_url) as img_resp:
                    if img_resp.status == 200:
                        return await img_resp.read()
                    logging.error("Image download failed: %s", img_resp.status)
                    return None
    except asyncio.TimeoutError:
        logging.error("fal.ai request timed out")
    except Exception as exc:
        logging.exception("fal.ai call failed: %s", exc)
    return None


async def generate_cat_image(
    perplexity_key: str, prompt: str
) -> Optional[bytes]:
    """
    Full pipeline:
    1. Enhance prompt via Perplexity sonar-pro
    2. Generate image via fal.ai FLUX Schnell
    3. Fall back to placeholder cat on any failure
    """
    fal_key = os.getenv("FAL_KEY", "")
    if not fal_key:
        logging.error("FAL_KEY env var is not set")
        return await _fetch_placeholder_cat()

    # Step 1: enhance the user prompt
    enhanced_prompt = await _enhance_prompt(perplexity_key, prompt)
    logging.info("Enhanced prompt: %s", enhanced_prompt)

    # Step 2: generate image
    image_bytes = await _generate_with_fal(fal_key, enhanced_prompt)
    if image_bytes:
        return image_bytes

    # Step 3: fallback
    logging.warning("fal.ai generation failed, using placeholder cat")
    return await _fetch_placeholder_cat()
