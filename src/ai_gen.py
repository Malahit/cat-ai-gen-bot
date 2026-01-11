"""
AI image generation using Perplexity API
"""
import os
import logging
import aiohttp

logger = logging.getLogger(__name__)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


async def generate_cat_image() -> str:
    """
    Generate a cat image using Perplexity API
    
    Returns:
        str: URL of the generated image
    """
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates creative cat image descriptions."
            },
            {
                "role": "user",
                "content": "Generate a unique and creative description for an AI cat image"
            }
        ],
        "max_tokens": 150,
        "temperature": 0.8,
        "top_p": 0.9
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(PERPLEXITY_API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    description = data["choices"][0]["message"]["content"]
                    logger.info(f"Generated cat description: {description}")
                    
                    # In a real implementation, you would use this description
                    # to generate an actual image using DALL-E, Stable Diffusion, etc.
                    # For demo purposes, return a placeholder cat image URL
                    return "https://cataas.com/cat"
                else:
                    logger.error(f"Perplexity API error: {response.status}")
                    raise Exception(f"API error: {response.status}")
    except Exception as e:
        logger.error(f"Error calling Perplexity API: {e}")
        raise


async def generate_cat_description() -> str:
    """
    Generate a creative cat description using Perplexity API
    
    Returns:
        str: Generated description
    """
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are a creative writer specializing in cat descriptions."
            },
            {
                "role": "user",
                "content": "Create a unique, whimsical description of a fictional cat in 2-3 sentences."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.9
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(PERPLEXITY_API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"API error: {response.status}")
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        raise
