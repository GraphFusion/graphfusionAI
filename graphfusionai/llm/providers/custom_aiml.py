"""
Custom AI/ML API provider implementation
"""

from typing import Dict, Any, Optional, List
from ..base import LLMProvider
import os
from openai import AsyncOpenAI

class AIMLProvider(LLMProvider):
    """AI/ML API provider using OpenAI SDK"""

    # Maximum tokens allowed by the API
    MAX_TOKENS_LIMIT = 512

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("AIML_API_KEY"),
            base_url=base_url or os.getenv("AIML_API_URL", "https://api.aimlapi.com/v1")
        )

    async def complete(self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate completion using AI/ML API"""
        # Ensure max_tokens doesn't exceed limit
        max_tokens = min(max_tokens or self.MAX_TOKENS_LIMIT, self.MAX_TOKENS_LIMIT)

        response = await self.client.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].text.strip()

    async def chat(self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate chat completion using AI/ML API"""
        # Ensure max_tokens doesn't exceed limit
        max_tokens = min(max_tokens or self.MAX_TOKENS_LIMIT, self.MAX_TOKENS_LIMIT)

        response = await self.client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content.strip()

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using AI/ML API"""
        response = await self.client.embeddings.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            input=text
        )
        return response.data[0].embedding