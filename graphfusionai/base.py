"""Base classes for the GraphFusionAI framework"""

from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel

class Role(BaseModel):
    """Agent role definition"""
    name: str
    capabilities: List[str]
    description: str

class Agent:
    """Base agent class"""
    
    def __init__(self, name: str, role: Role):
        self.name = name
        self.role = role
        self.capabilities: Dict[str, Callable] = {}
        self.llm_provider = None
        self.memory = None
        
    def register_capability(self, name: str, func: Callable, description: str = None):
        """Register a new capability"""
        self.capabilities[name] = func
        if name not in self.role.capabilities:
            self.role.capabilities.append(name)
            
    async def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming task"""
        task_type = task.get("type")
        if task_type in self.capabilities:
            return await self.capabilities[task_type](**task.get("data", {}))
        return await self._process_task(task)
        
    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task that doesn't match a specific capability"""
        raise NotImplementedError("Agents must implement _process_task")
