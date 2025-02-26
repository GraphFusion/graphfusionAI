"""
Base classes for LLM integration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def complete(self, 
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate completion for the given prompt"""
        pass
    
    @abstractmethod
    async def chat(self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate chat completion for the given messages"""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for the given text"""
        pass
