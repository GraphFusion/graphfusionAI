"""
OpenAI provider implementation
"""

from typing import Dict, Any, Optional, List
from ..base import LLMProvider
import os
import openai
from openai import AsyncOpenAI

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def complete(self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate completion using OpenAI API"""
        response = await self.client.completions.create(
            model="gpt-3.5-turbo-instruct",
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
        """Generate chat completion using OpenAI API"""
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content.strip()
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API"""
        response = await self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
