
"""
Modular and Simplified MAS Framework Example
"""

import asyncio
import logging
from typing import Dict, Any, List
from graphfusionai import Agent, Role
from graphfusionai.llm import AIMLProvider, PromptTemplate
from graphfusionai.memory import Memory
from graphfusionai.knowledge_graph import KnowledgeGraph, Node
from graphfusionai.orchestration import AgentOrchestrator, AgentTemplate, ConditionalTask
from graphfusionai.task_orchestrator import Task

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Global LLM Provider 
LLM_PROVIDER = AIMLProvider(
    api_key="e098f023457f4038b10d83f5d9411d5d",
    base_url="https://api.aimlapi.com/v1"
)

class BaseAgent(Agent):
    """Base class for all agents to reuse common components"""
    
    def __init__(self, prompt_templates: List[PromptTemplate], **kwargs):
        super().__init__(**kwargs)
        self.memory = Memory()
        self.knowledge_graph = KnowledgeGraph()
        self.set_llm_provider(LLM_PROVIDER)

        for template in prompt_templates:
            self.add_prompt_template(template)

class AnalystAgent(BaseAgent):
    """Agent that analyzes data using LLM"""

    def __init__(self, **kwargs):
        if 'role' not in kwargs:
            kwargs['role'] = Role(
                name='analyst',
                capabilities=['analyze'],
                description='Analyzes data using LLM'
            )
        prompt_templates = [
            PromptTemplate(
                name='analyze',
                template='Analyze this data and provide insights: {data}',
                description='Template for analysis'
            )
        ]
        super().__init__(prompt_templates=prompt_templates, **kwargs)

    async def _process_task(self, task: dict) -> dict:
        data = task.get("data", {})
        analysis = await self.complete(self.format_prompt("analyze", data=str(data)))
        
        self.memory.store(f"analysis_{task['id']}", analysis)
        self.knowledge_graph.add_node(Node(
            id=f"analysis_{task['id']}",
            type="analysis",
            properties={"result": analysis}
        ))

        return {"analysis": analysis}

async def main():
    orchestrator = AgentOrchestrator()
    
    # Register agent templates
    orchestrator.register_template("analyst", AgentTemplate(
        role=Role(name="analyst", capabilities=["analyze"], description="Analyzes data"),
        agent_class=AnalystAgent
    ))
    
    # Define workflow
    workflow = [
        ConditionalTask(
            task=Task(
                id="analysis_task",
                type="analyze",
                data={"text": "Sample data for analysis"},
                assigned_to="analyst"
            ),
            next_tasks=[]
        )
    ]
    
    try:
        logger.info("Starting workflow execution...")
        results = await orchestrator.execute_conditional(workflow)
        
        logger.info("\nWorkflow Results:")
        for result in results:
            logger.info(f"Task result: {result}")
            
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
