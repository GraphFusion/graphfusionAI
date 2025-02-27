"""
LiteLLM provider implementation supporting 100+ LLM providers
"""

import json
import logging
import os
import sys
import threading
import warnings
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
import litellm
from litellm import Choices
from litellm.utils import supports_response_schema

from ..base import LLMProvider

load_dotenv()

logger = logging.getLogger(__name__)

# Default context window sizes for various models
LLM_CONTEXT_WINDOW_SIZES = {
    # openai
    "gpt-4": 8192,
    "gpt-4-turbo": 128000,
    # anthropic
    "claude-3-opus": 200000,
    "claude-3-sonnet": 200000,
    "claude-2.1": 200000,
    # gemini
    "gemini-pro": 32000,
    "gemini-1.5-pro": 2097152,
    # mistral
    "mistral-small": 32000,
    "mistral-medium": 32000,
    "mistral-large": 32000,
}

DEFAULT_CONTEXT_WINDOW_SIZE = 8192
CONTEXT_WINDOW_USAGE_RATIO = 0.75

class FilteredStream:
    """Filter out unwanted LiteLLM messages from stdout/stderr"""
    def __init__(self, original_stream):
        self._original_stream = original_stream
        self._lock = threading.Lock()

    def write(self, s) -> int:
        with self._lock:
            # Filter out extraneous messages from LiteLLM
            if ("Give Feedback / Get Help: https://github.com/BerriAI/litellm/issues/new" in s
                or "LiteLLM.Info: If you need to debug this error, use `litellm.set_verbose=True`" in s):
                return 0
            return self._original_stream.write(s)

    def flush(self):
        with self._lock:
            return self._original_stream.flush()

@contextmanager
def suppress_warnings():
    """Context manager to suppress warnings and filter streams"""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        warnings.filterwarnings("ignore", message="open_text is deprecated*", category=DeprecationWarning)

        # Redirect stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = FilteredStream(old_stdout)
        sys.stderr = FilteredStream(old_stderr)
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

class LiteLLMProvider(LLMProvider):
    """LiteLLM-based provider supporting 100+ LLM providers"""

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Initialize LiteLLM provider
        
        Args:
            model: Model identifier (e.g. "gpt-4", "claude-3", "gemini-pro")
            api_key: API key for the provider
            base_url: Optional base URL override
            timeout: Optional timeout in seconds
            temperature: Optional temperature (0-1)
            max_tokens: Optional max tokens for completion
            **kwargs: Additional provider-specific parameters
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.additional_params = kwargs
        
        # Configure LiteLLM
        litellm.drop_params = True
        self.set_env_callbacks()

    async def complete(self, prompt: str) -> str:
        """Generate completion using LiteLLM
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated completion text
            
        Raises:
            Exception if completion fails
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat completion using LiteLLM
        
        Args:
            messages: List of message dicts with role and content
            
        Returns:
            Generated response text
            
        Raises:
            Exception if chat completion fails
        """
        with suppress_warnings():
            try:
                # Prepare parameters
                params = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "timeout": self.timeout,
                    "api_key": self.api_key,
                    "api_base": self.base_url,
                    "stream": False,
                    **self.additional_params
                }

                # Remove None values
                params = {k: v for k, v in params.items() if v is not None}

                # Make completion call
                response = litellm.completion(**params)
                
                # Extract response text
                response_message = Choices(response.choices)[0].message
                return response_message.content or ""

            except Exception as e:
                logger.error(f"LiteLLM chat completion failed: {str(e)}")
                raise

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using LiteLLM
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding floats
            
        Raises:
            Exception if embedding fails
        """
        with suppress_warnings():
            try:
                response = litellm.embedding(
                    model=self.model,
                    input=text,
                    api_key=self.api_key,
                    api_base=self.base_url
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"LiteLLM embedding failed: {str(e)}")
                raise

    def get_context_window_size(self) -> int:
        """Get context window size for model
        
        Returns:
            Context window size in tokens, using 75% of max
        """
        for key, value in LLM_CONTEXT_WINDOW_SIZES.items():
            if self.model.startswith(key):
                return int(value * CONTEXT_WINDOW_USAGE_RATIO)
        return int(DEFAULT_CONTEXT_WINDOW_SIZE * CONTEXT_WINDOW_USAGE_RATIO)

    def set_env_callbacks(self):
        """Set LiteLLM callbacks from environment variables"""
        with suppress_warnings():
            success_callbacks_str = os.environ.get("LITELLM_SUCCESS_CALLBACKS", "")
            success_callbacks = []
            if success_callbacks_str:
                success_callbacks = [cb.strip() for cb in success_callbacks_str.split(",") if cb.strip()]

            failure_callbacks_str = os.environ.get("LITELLM_FAILURE_CALLBACKS", "")
            failure_callbacks = []
            if failure_callbacks_str:
                failure_callbacks = [cb.strip() for cb in failure_callbacks_str.split(",") if cb.strip()]

            litellm.success_callback = success_callbacks
            litellm.failure_callback = failure_callbacks

    def supports_function_calling(self) -> bool:
        """Check if model supports function calling"""
        try:
            params = litellm.get_supported_openai_params(model=self.model)
            return "response_format" in params
        except Exception as e:
            logger.error(f"Failed to get supported params: {str(e)}")
            return False
