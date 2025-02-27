"""Base agent implementation with LLM capabilities"""

from typing import List, Dict, Any, Optional, Callable, TypeVar, Union, Type
from pydantic import BaseModel, PrivateAttr
from uuid import uuid4
import logging
from rich.console import Console
import inspect
from functools import wraps
import asyncio
from contextlib import asynccontextmanager

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

    def validate_capabilities(self, tools: List[str]) -> bool:
        """Validate that all required capabilities are available"""
        return all(cap in tools for cap in self.capabilities)

class Tool(BaseModel):
    """Tool definition for agent capabilities"""
    name: str
    description: str
    func: Callable
    async_handler: bool = False
    timeout: Optional[float] = None
    
    def validate(self) -> bool:
        """Validate tool configuration"""
        if not callable(self.func):
            return False
        if self.async_handler and not inspect.iscoroutinefunction(self.func):
            return False
        return True

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
    _active_tasks: Dict[str, asyncio.Task] = PrivateAttr(default_factory=dict)

    # LLM-related attributes
    _llm_provider: Optional[LLMProvider] = PrivateAttr(default=None)
    _prompt_manager: Optional[PromptManager] = PrivateAttr(default=None)
    _conversation: Optional[ConversationManager] = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self._logger = logging.getLogger(f"Agent_{self.name}")
        self._setup_logging()

    def _setup_logging(self):
        """Setup agent-specific logging"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def register_tool(self, tool: Tool) -> bool:
        """Register a new tool with validation"""
        try:
            if not tool.validate():
                self._logger.error(f"Invalid tool configuration: {tool.name}")
                return False
                
            self._tools[tool.name] = tool
            self._logger.info(f"Tool registered: {tool.name}")
            return True
        except Exception as e:
            self._logger.error(f"Error registering tool {tool.name}: {str(e)}")
            return False

    @asynccontextmanager
    async def _tool_execution_context(self, tool_name: str):
        """Context manager for tool execution with timeout and cleanup"""
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
            
        task_id = str(uuid4())
        try:
            yield task_id
        finally:
            if task_id in self._active_tasks:
                task = self._active_tasks[task_id]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self._active_tasks[task_id]

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool with proper error handling and timeout"""
        async with self._tool_execution_context(tool_name) as task_id:
            tool = self._tools[tool_name]
            
            try:
                if tool.async_handler:
                    # Extract the first value if kwargs has only one item
                    if len(kwargs) == 1 and "data" in kwargs:
                        kwargs = kwargs["data"]
                        
                    task = asyncio.create_task(tool.func(kwargs))
                else:
                    task = asyncio.create_task(
                        asyncio.to_thread(tool.func, kwargs)
                    )
                    
                self._active_tasks[task_id] = task
                
                if tool.timeout:
                    result = await asyncio.wait_for(task, timeout=tool.timeout)
                else:
                    result = await task
                    
                return {
                    "status": "success",
                    "result": result,
                    "tool": tool_name
                }
                
            except asyncio.TimeoutError:
                self._logger.error(f"Tool {tool_name} timed out")
                return {
                    "status": "error",
                    "error": f"Tool execution timed out after {tool.timeout}s",
                    "tool": tool_name
                }
            except Exception as e:
                self._logger.error(f"Error executing tool {tool_name}: {str(e)}")
                return {
                    "status": "error",
                    "error": str(e),
                    "tool": tool_name
                }

    async def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming task with proper validation"""
        try:
            # Validate task format
            if not isinstance(task, dict):
                raise ValueError("Task must be a dictionary")
                
            if "type" not in task:
                raise ValueError("Task must have a type")
                
            # Check if we have required capabilities
            if task["type"] not in self._tools:
                raise ValueError(f"Agent lacks required tool: {task['type']}")
                
            # Execute task
            result = await self._process_task(task)
            return {
                "status": "success",
                "result": result,
                "task_id": task.get("id", str(uuid4()))
            }
            
        except Exception as e:
            self._logger.error(f"Error handling task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_id": task.get("id", str(uuid4()))
            }

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        """Process task by executing appropriate tool"""
        tool_name = task["type"]
        data = task.get("data", {})
        
        # If data is a dictionary with a single key matching the parameter name,
        # extract the value to pass directly
        if len(data) == 1:
            param_name = next(iter(data))
            if param_name in inspect.signature(self._tools[tool_name].func).parameters:
                data = data[param_name]
                
        result = await self.execute_tool(tool_name, data=data)
        return result

    async def cleanup(self):
        """Cleanup agent resources"""
        # Cancel all active tasks
        for task_id, task in list(self._active_tasks.items()):
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self._active_tasks[task_id]
            
        # Clear memory and tools
        self._memory.clear()
        self._tools.clear()
        
        # Cleanup LLM resources if present
        if self._llm_provider:
            await self._llm_provider.cleanup()
        if self._conversation:
            self._conversation.clear()
            
        self._logger.info("Agent resources cleaned up")