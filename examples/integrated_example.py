"""
Updated integrated example ensuring all agents have a memory field.
"""

import asyncio
import logging
from typing import Dict, Any
from graphfusionai import Agent, Role
from graphfusionai.llm import AIMLProvider, PromptTemplate
from graphfusionai.memory import Memory
from graphfusionai.knowledge_graph import KnowledgeGraph, Node
from graphfusionai.orchestration import AgentOrchestrator, AgentTemplate, ConditionalTask
from graphfusionai.task_orchestrator import Task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API key once for all agents
API_KEY = "e098f023457f4038b10d83f5d9411d5d"
BASE_URL = "https://api.aimlapi.com/v1"

class BaseLLMAgent(Agent):
    """Base agent ensuring memory and knowledge graph exist for all agents."""

    def __init__(self, name: str, **kwargs):
        logger.info(f"Initializing {name}...")

        # Ensure memory and knowledge graph are set up BEFORE calling super()
        self.memory = Memory()
        self.knowledge_graph = KnowledgeGraph()

        # Now call the parent constructor
        super().__init__(name=name, **kwargs)

        # Ensure LLM provider is initialized
        self.llm_provider = AIMLProvider(api_key=API_KEY, base_url=BASE_URL)
        self.set_llm_provider(self.llm_provider)

        logger.info(f"{name} initialized with memory and knowledge graph.")

class AnalystAgent(BaseLLMAgent):
    """Agent for analyzing data using LLM"""

    def __init__(self, name="AnalystAgent", **kwargs):
        super().__init__(name=name, **kwargs)
        self.add_prompt_template(PromptTemplate(
            name="analyze",
            template="Analyze this data and provide insights: {data}",
            description="Template for analysis"
        ))

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Fix: Access the proper field in task data, with fallback
        if isinstance(task["data"], dict) and "text" in task["data"]:
            data = task["data"]["text"]
        else:
            data = task["data"]
            
        # Add better error handling
        try:
            analysis = await self.complete(
                self.format_prompt("analyze", data=str(data))
            )

            # Store in memory
            self.memory.store(f"analysis_{task['id']}", analysis)

            node = Node(
                id=f"analysis_{task['id']}",
                type="analysis",
                properties={"result": analysis}
            )
            self.knowledge_graph.add_node(node)

            return {"analysis": analysis}
        except Exception as e:
            logger.error(f"Error in AnalystAgent processing: {str(e)}")
            return {"error": str(e)}

class ResearchAgent(BaseLLMAgent):
    """Agent for performing research tasks"""

    def __init__(self, name="ResearchAgent", **kwargs):
        super().__init__(name=name, **kwargs)

        self.add_prompt_template(PromptTemplate(
            name="research",
            template="Research this topic and summarize: {topic}",
            description="Template for research"
        ))

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Add better error handling and validation
            if isinstance(task["data"], dict) and "topic" in task["data"]:
                topic = task["data"]["topic"]
            else:
                logger.warning(f"Task data does not contain topic: {task}")
                topic = str(task["data"])
                
            research = await self.complete(
                self.format_prompt("research", topic=topic)
            )

            self.memory.store(f"research_{task['id']}", research)
            return {"research": research}
        except Exception as e:
            logger.error(f"Error in ResearchAgent processing: {str(e)}")
            return {"error": str(e)}

async def main():
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()

    # Register agent templates
    orchestrator.register_template("analyst", AgentTemplate(
        role=Role(
            name="analyst",
            capabilities=["analyze"],
            description="Analyzes data using LLM"
        ),
        agent_class=AnalystAgent
    ))

    orchestrator.register_template("researcher", AgentTemplate(
        role=Role(
            name="researcher",
            capabilities=["research"],
            description="Performs research tasks"
        ),
        agent_class=ResearchAgent
    ))

    # Define workflow with improved task connection
    workflow = [
        ConditionalTask(
            task=Task(
                id="research_task",
                type="research",
                data={"topic": "AI and Knowledge Graphs"},
                assigned_to="researcher"
            ),
            next_tasks=[{
                "id": "analysis_task",
                "type": "analyze",
                "data_source": "research_task",  # Specify source of data
                "agent_type": "analyst"
            }]
        )
    ]

    try:
        logger.info("Starting workflow execution...")
        # Add more debug logs
        logger.info(f"Workflow configuration: {workflow}")
        results = await orchestrator.execute_conditional(workflow)

        logger.info("\nWorkflow Results:")
        for result in results:
            logger.info(f"Task result: {result}")

    except Exception as e:
        logger.error(f"Error in workflow: {str(e)}", exc_info=True)  # Include full traceback

if __name__ == "__main__":
    asyncio.run(main())