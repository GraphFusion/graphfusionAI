"""Pre-built agent templates for common use cases"""

from typing import Dict, Any, List
from .factory import AgentTemplate
from ..base import Agent
from ..llm import LLMAgent
from ..memory import VectorMemory

class ResearchAgent(Agent):
    """Research specialist agent implementation"""
    async def research(self, topic: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(f"Research about {topic}")
        
    async def analyze(self, data: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(f"Analyze this data: {data}")
        
    async def summarize(self, text: str) -> str:
        return await self.llm_provider.complete(f"Summarize this: {text}")

class AssistantAgent(LLMAgent):
    """General purpose assistant agent"""
    async def chat(self, message: str) -> str:
        return await self.llm_provider.chat(message)
        
    async def help(self, topic: str) -> str:
        return await self.llm_provider.complete(f"Help with {topic}")
        
    async def explain(self, concept: str) -> str:
        return await self.llm_provider.complete(f"Explain {concept}")

class ExecutorAgent(Agent):
    """Task execution specialist"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = VectorMemory()
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        result = await self._process_task(task)
        self.memory.store(f"task_{task['id']}", result)
        return result
        
    async def monitor(self, task_id: str) -> Dict[str, Any]:
        return self.memory.retrieve(f"task_{task_id}")
        
    async def report(self, task_ids: List[str]) -> Dict[str, Any]:
        results = []
        for task_id in task_ids:
            result = await self.monitor(task_id)
            if result:
                results.append(result)
        return {"task_results": results}

# Register templates
BUILT_IN_TEMPLATES = {
    "researcher": AgentTemplate(
        name="researcher",
        capabilities=["research", "analyze", "summarize"],
        description="Research specialist agent",
        base_class=ResearchAgent
    ),
    "assistant": AgentTemplate(
        name="assistant", 
        capabilities=["chat", "help", "explain"],
        description="General purpose assistant agent",
        base_class=AssistantAgent
    ),
    "executor": AgentTemplate(
        name="executor",
        capabilities=["execute", "monitor", "report"],
        description="Task execution specialist",
        base_class=ExecutorAgent
    )
}
