"""
Multi-Agent System Framework with Knowledge Graph Integration
"""

from .base import Agent, Role
from .agents.factory import AgentFactory, AgentConfig
from .agents.templates import ResearchAgent, AssistantAgent, ExecutorAgent
from .agents.specialized import (
    DataScientistAgent,
    DeveloperAgent,
    ProductManagerAgent,
    SecurityAgent
)
from graphfusionai.knowledge_graph import KnowledgeGraph, Node, Edge
from graphfusionai.task_orchestrator import TaskOrchestrator, Task
from graphfusionai.communication import Message, CommunicationBus
from graphfusionai.memory import Memory
from graphfusionai.team import Team
from graphfusionai.ontology import Ontology
from graphfusionai.llm.base import LLMProvider 

__version__ = "0.1.3"
__all__ = [
    "Agent",
    "Role",
    "AgentFactory",
    "AgentConfig",
    "ResearchAgent",
    "AssistantAgent",
    "ExecutorAgent",
    "DataScientistAgent",
    "DeveloperAgent",
    "ProductManagerAgent",
    "SecurityAgent",
    "KnowledgeGraph",
    "Node",
    "Edge",
    "TaskOrchestrator",
    "Task",
    "Message",
    "CommunicationBus",
    "Team",
    "Memory",
    "Ontology",
    "LLMProvider" 
]