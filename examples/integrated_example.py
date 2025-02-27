"""
Updated integrated example using chat completion API.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from graphfusionai import Agent, Role, Tool
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
    memory: Memory
    knowledge_graph: KnowledgeGraph
    llm_provider: Optional[AIMLProvider] = None

    def __init__(self, name: str, **kwargs):
        logger.info(f"Initializing {name}...")

        # Initialize memory and knowledge graph
        kwargs["memory"] = Memory()
        kwargs["knowledge_graph"] = KnowledgeGraph()

        # Now call the parent constructor
        super().__init__(name=name, **kwargs)

        # Ensure LLM provider is initialized
        self.llm_provider = AIMLProvider(api_key=API_KEY, base_url=BASE_URL)

        logger.info(f"{name} initialized with memory and knowledge graph.")

    async def chat_complete(self, messages: List[Dict[str, str]]) -> str:
        """Complete using chat API"""
        if not self.llm_provider:
            raise ValueError("LLM provider not initialized")
        try:
            return await self.llm_provider.chat(messages)
        except Exception as e:
            logger.error(f"Error in LLM chat completion: {str(e)}")
            if "400" in str(e):
                return "I apologize, but I encountered an error processing your request. The prompt may be too long or contain invalid characters."
            return "I apologize, but I encountered an error processing your request."

class AnalystAgent(BaseLLMAgent):
    """Agent for analyzing data using LLM"""

    def __init__(self, name="AnalystAgent", **kwargs):
        super().__init__(name=name, **kwargs)
        self._system_prompt = "You are an expert data analyst. Your task is to analyze data and provide key insights."

        # Register analyze tool
        self.register_tool(Tool(
            name="analyze",
            description="Analyze data using LLM",
            func=self._process_task,
            async_handler=True
        ))

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Fix: Access the proper field in task data, with fallback
        if isinstance(task["data"], dict) and "text" in task["data"]:
            data = task["data"]["text"]
        else:
            data = task["data"]
            
        # Add better error handling
        try:
            messages = [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": f"Please analyze this data: {data}"}
            ]
            
            analysis = await self.chat_complete(messages)

            # Store in memory
            self.memory.store(f"analysis_{task['id']}", analysis)

            node = Node(
                id=f"analysis_{task['id']}",
                type="analysis",
                properties={"result": analysis}
            )
            self.knowledge_graph.add_node(node)

            return {"status": "success", "result": analysis}
        except Exception as e:
            logger.error(f"Error in AnalystAgent processing: {str(e)}")
            return {"status": "error", "error": str(e)}

class ResearchAgent(BaseLLMAgent):
    """Agent for performing research tasks"""

    def __init__(self, name="ResearchAgent", **kwargs):
        super().__init__(name=name, **kwargs)
        self._system_prompt = "You are an expert researcher. Your task is to research topics and provide comprehensive summaries."

        # Register research tool
        self.register_tool(Tool(
            name="research",
            description="Research topics using LLM",
            func=self._process_task,
            async_handler=True
        ))

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Add better error handling and validation
            if isinstance(task["data"], dict) and "topic" in task["data"]:
                topic = task["data"]["topic"]
            else:
                logger.warning(f"Task data does not contain topic: {task}")
                topic = str(task["data"])

            messages = [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": f"Please research this topic: {topic}"}
            ]
                
            research = await self.chat_complete(messages)

            self.memory.store(f"research_{task['id']}", research)
            return {"status": "success", "result": research}
        except Exception as e:
            logger.error(f"Error in ResearchAgent processing: {str(e)}")
            return {"status": "error", "error": str(e)}

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

    # Create agents
    researcher = orchestrator.create_agent("researcher")
    analyst = orchestrator.create_agent("analyst")

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
                "data": {"text": "Research on AI and Knowledge Graphs"},
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