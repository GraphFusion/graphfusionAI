"""Agent factory and template system for easy agent creation"""

from typing import Dict, Any, Optional, Type, List
from pydantic import BaseModel
from ..base import Agent, Role
from ..memory import BaseMemory, VectorMemory
from ..llm import LLMProvider
from ..tools import ToolRegistry

class AgentConfig(BaseModel):
    """Configuration for agent creation"""
    name: str
    capabilities: List[str]
    description: Optional[str] = None
    llm_config: Optional[Dict[str, Any]] = None
    memory_config: Optional[Dict[str, Any]] = None
    tools_config: Optional[Dict[str, Any]] = None

class AgentTemplate:
    """Base class for agent templates"""
    def __init__(
        self,
        name: str,
        capabilities: List[str],
        description: str,
        base_class: Type[Agent] = Agent
    ):
        self.name = name
        self.capabilities = capabilities
        self.description = description
        self.base_class = base_class

    def create(self, config: AgentConfig) -> Agent:
        """Create an agent instance from this template"""
        role = Role(
            name=self.name,
            capabilities=self.capabilities + config.capabilities,
            description=config.description or self.description
        )
        
        agent = self.base_class(name=config.name, role=role)
        
        # Configure LLM if specified
        if config.llm_config:
            agent.llm_provider = LLMProvider.from_config(config.llm_config)
            
        # Configure memory if specified
        if config.memory_config:
            agent.memory = VectorMemory.from_config(config.memory_config)
            
        # Configure tools if specified
        if config.tools_config:
            registry = ToolRegistry.from_config(config.tools_config)
            for tool in registry.list_tools():
                agent.register_tool(tool)
                
        return agent

class AgentFactory:
    """Factory for creating agents from templates"""
    
    def __init__(self):
        self.templates: Dict[str, AgentTemplate] = {}
        self._register_default_templates()
        
    def _register_default_templates(self):
        """Register built-in templates"""
        self.register_template(AgentTemplate(
            name="researcher",
            capabilities=["research", "analyze", "summarize"],
            description="Research specialist agent"
        ))
        
        self.register_template(AgentTemplate(
            name="assistant",
            capabilities=["chat", "help", "explain"],
            description="General purpose assistant agent"
        ))
        
        self.register_template(AgentTemplate(
            name="executor",
            capabilities=["execute", "monitor", "report"],
            description="Task execution specialist"
        ))
        
    def register_template(self, template: AgentTemplate):
        """Register a new agent template"""
        self.templates[template.name] = template
        
    def create_agent(
        self,
        template_name: str,
        config: AgentConfig
    ) -> Agent:
        """Create an agent from a template"""
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
            
        template = self.templates[template_name]
        return template.create(config)
        
    def list_templates(self) -> List[str]:
        """List available template names"""
        return list(self.templates.keys())
        
    @classmethod
    def easy_agent(
        cls,
        name: str,
        capabilities: List[str],
        template: str = "assistant",
        **kwargs
    ) -> Agent:
        """Quick one-line agent creation"""
        factory = cls()
        config = AgentConfig(
            name=name,
            capabilities=capabilities,
            **kwargs
        )
        return factory.create_agent(template, config)
