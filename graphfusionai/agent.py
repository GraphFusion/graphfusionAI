"""Base agent implementation with LLM capabilities"""

from typing import List, Dict, Any, Optional, Callable, TypeVar, Union, Type
from pydantic import BaseModel, PrivateAttr
from uuid import uuid4
import logging
from rich.console import Console
import inspect
from functools import wraps

from .llm import (
    LLMProvider, PromptManager, ConversationManager,
    PromptTemplate
)

console = Console()
T = TypeVar('T')

class Role(BaseModel):
    """Define agent roles and capabilities"""
    name: str
    capabilities: List[str]
    description: str

class Tool(BaseModel):
    """Tool definition for agent capabilities"""
    name: str
    description: str
    func: Callable
    async_handler: bool = False

class Agent(BaseModel):
    """Base agent class with core functionality"""
    id: str = str(uuid4())
    name: str
    role: Role
    state: Dict[str, Any] = {}

    # Private attributes
    _logger: logging.Logger = PrivateAttr()
    _memory: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _tools: Dict[str, Tool] = PrivateAttr(default_factory=dict)

    # LLM-related attributes
    _llm_provider: Optional[LLMProvider] = PrivateAttr(default=None)
    _prompt_manager: Optional[PromptManager] = PrivateAttr(default=None)
    _conversation: Optional[ConversationManager] = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self._logger = logging.getLogger(f"Agent-{self.name}")
        self._memory = {}
        self._tools = {}

        # Initialize LLM components if provider is set
        if "_llm_provider" in data:
            self._llm_provider = data["_llm_provider"]
            self._prompt_manager = PromptManager()
            self._conversation = ConversationManager()

    @classmethod
    def create(cls, name: str, role: Optional[Role] = None, **kwargs):
        """Decorator for creating agent classes"""
        def decorator(cls_: Type[T]) -> Type[T]:
            if not role:
                # Create default role from class attributes
                capabilities = [
                    name for name, _ in inspect.getmembers(cls_, predicate=inspect.ismethod)
                    if not name.startswith('_')
                ]
                role_ = Role(
                    name=cls_.__name__.lower(),
                    capabilities=capabilities,
                    description=cls_.__doc__ or f"Agent for {cls_.__name__}"
                )
            else:
                role_ = role

            @wraps(cls_)
            def wrapped(*args, **kwargs):
                # Ensure required fields are passed
                kwargs['name'] = name
                kwargs['role'] = role_
                instance = cls_(*args, **kwargs)
                return instance
            return wrapped
        return decorator

    def tool(self, name: Optional[str] = None, description: Optional[str] = None):
        """Decorator for registering tools"""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            tool_desc = description or func.__doc__ or f"Tool {tool_name}"
            is_async = inspect.iscoroutinefunction(func)

            self._tools[tool_name] = Tool(
                name=tool_name,
                description=tool_desc,
                func=func,
                async_handler=is_async
            )
            return func
        return decorator

    async def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming tasks based on agent capabilities"""
        if task["type"] not in self.role.capabilities:
            raise ValueError(f"Task type {task['type']} not supported by agent {self.name}")

        try:
            result = await self._process_task(task)
            return {
                "status": "success",
                "agent_id": self.id,
                "result": result
            }
        except Exception as e:
            self._logger.error(f"Error processing task: {str(e)}")
            return {
                "status": "error",
                "agent_id": self.id,
                "error": str(e)
            }

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        """Process task based on type"""
        # Override this method in specific agent implementations
        raise NotImplementedError

    def update_state(self, state_update: Dict[str, Any]):
        """Update agent's internal state"""
        self.state.update(state_update)
        self._logger.debug(f"State updated: {self.state}")

    def remember(self, key: str, value: Any):
        """Store information in agent's memory"""
        self._memory[key] = value

    def recall(self, key: str) -> Optional[Any]:
        """Retrieve information from agent's memory"""
        return self._memory.get(key)

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        if tool_name not in self._tools:
            raise ValueError(f"Tool {tool_name} not found")

        tool = self._tools[tool_name]
        if tool.async_handler:
            return await tool.func(**kwargs)
        return tool.func(**kwargs)

    # LLM-related methods
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion using LLM"""
        if not self._llm_provider:
            raise ValueError("LLM provider not configured")
        return await self._llm_provider.complete(prompt, **kwargs)

    async def chat(self, 
        messages: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate chat completion using LLM"""
        if not self._llm_provider:
            raise ValueError("LLM provider not configured")

        if messages is None and self._conversation:
            messages = self._conversation.format_for_llm()

        response = await self._llm_provider.chat(messages, **kwargs)

        if self._conversation:
            self._conversation.add_message("assistant", response)

        return response

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using LLM"""
        if not self._llm_provider:
            raise ValueError("LLM provider not configured")
        return await self._llm_provider.embed(text)

    def set_llm_provider(self, provider: LLMProvider):
        """Set LLM provider for the agent"""
        self._llm_provider = provider
        if not self._prompt_manager:
            self._prompt_manager = PromptManager()
        if not self._conversation:
            self._conversation = ConversationManager()

    def add_prompt_template(self, template: PromptTemplate):
        """Add prompt template"""
        if not self._prompt_manager:
            self._prompt_manager = PromptManager()
        self._prompt_manager.add_template(template)

    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format prompt template"""
        if not self._prompt_manager:
            raise ValueError("Prompt manager not configured")
        return self._prompt_manager.format_prompt(template_name, **kwargs)