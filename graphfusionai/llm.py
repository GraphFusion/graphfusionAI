"""
High-level LLM interface supporting multiple providers
"""

import os
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv

from llm.providers.litellm_provider import LiteLLMProvider
from llm.providers.custom_aiml import AIMLProvider

load_dotenv()

class LLM:
    """High-level LLM interface supporting multiple providers"""
    
    def __init__(
        self,
        model: str = "gpt-4",
        provider: str = "litellm",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Initialize LLM interface
        
        Args:
            model: Model identifier (e.g. "gpt-4", "claude-3", "gemini-pro")
            provider: Provider to use ("litellm" or "custom")
            api_key: API key (defaults to env var)
            base_url: Optional API base URL
            temperature: Temperature for generation (0-1)
            max_tokens: Max tokens for completion
            **kwargs: Additional provider-specific parameters
        """
        # Get API key from env if not provided
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")  # Default to OpenAI
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY")  # Try Anthropic
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")  # Try Google

        # Initialize appropriate provider
        if provider == "litellm":
            self._provider = LiteLLMProvider(
                model=model,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        else:  # Use custom provider for testing/development
            self._provider = AIMLProvider(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

    async def complete(self, prompt: str) -> str:
        """Generate completion for prompt
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated completion
        """
        return await self._provider.complete(prompt)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat completion
        
        Args:
            messages: List of message dicts with role and content
            
        Returns:
            Generated response
        """
        return await self._provider.chat(messages)

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        return await self._provider.embed(text)

    def get_context_window_size(self) -> int:
        """Get context window size for model"""
        return self._provider.get_context_window_size()

    def supports_function_calling(self) -> bool:
        """Check if model supports function calling"""
        return self._provider.supports_function_calling()
