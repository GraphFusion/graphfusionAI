"""Agent module initialization"""

from .factory import AgentFactory, AgentConfig
from .templates import ResearchAgent, AssistantAgent, ExecutorAgent
from .specialized import (
    DataScientistAgent,
    DeveloperAgent,
    ProductManagerAgent,
    SecurityAgent
)
from .decorators import capability, agent_template, auto_capabilities

__all__ = [
    "AgentFactory",
    "AgentConfig",
    "ResearchAgent",
    "AssistantAgent",
    "ExecutorAgent",
    "DataScientistAgent",
    "DeveloperAgent",
    "ProductManagerAgent",
    "SecurityAgent",
    "capability",
    "agent_template",
    "auto_capabilities"
]
