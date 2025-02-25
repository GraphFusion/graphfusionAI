import asyncio
from mas_framework import (
    Agent, Role, KnowledgeGraph, TaskOrchestrator,
    Message, CommunicationBus, Memory, Ontology
)
from mas_framework.task_orchestrator import Task  # Add Task import
from typing import Dict, Any
import logging
from rich.console import Console

console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define roles
researcher_role = Role(
    name="researcher",
    capabilities=["research", "analyze"],
    description="Performs research and analysis tasks"
)

processor_role = Role(
    name="processor",
    capabilities=["process", "transform"],
    description="Processes and transforms data"
)

# Create agents
class ResearchAgent(Agent):
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        if task["type"] == "research":
            return {"research_results": f"Research completed for {task['data']['topic']}"}
        elif task["type"] == "analyze":
            return {"analysis_results": f"Analysis completed for {task['data']['subject']}"}
        raise ValueError(f"Unsupported task type: {task['type']}")

class ProcessorAgent(Agent):
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        if task["type"] == "process":
            return {"processed_data": f"Processed {task['data']['input']}"}
        elif task["type"] == "transform":
            return {"transformed_data": f"Transformed {task['data']['input']}"}
        raise ValueError(f"Unsupported task type: {task['type']}")

async def main():
    # Initialize components
    kg = KnowledgeGraph()
    orchestrator = TaskOrchestrator()
    comm_bus = CommunicationBus()
    memory = Memory()

    # Create agents
    researcher = ResearchAgent(
        name="ResearchAgent1",
        role=researcher_role
    )

    processor = ProcessorAgent(
        name="ProcessorAgent1",
        role=processor_role
    )

    # Create tasks
    research_task = Task(
        id="task1",
        type="research",
        data={"topic": "AI Knowledge Graphs"},
        assigned_to=researcher.id
    )

    process_task = Task(
        id="task2",
        type="process",
        data={"input": "research_results"},
        assigned_to=processor.id
    )

    # Add tasks to orchestrator
    orchestrator.add_task(research_task)
    orchestrator.add_task(process_task)

    # Start communication bus
    comm_bus_task = asyncio.create_task(comm_bus.start())

    try:
        # Execute tasks
        result1 = await orchestrator.execute_task(researcher, research_task)
        console.print("[green]Research task completed:", result1)

        result2 = await orchestrator.execute_task(processor, process_task)
        console.print("[green]Process task completed:", result2)

        # Store results in memory
        memory.store("research_results", result1)
        memory.store("process_results", result2)

        # Retrieve results
        stored_research = memory.retrieve("research_results")
        console.print("[blue]Retrieved research results:", stored_research)
    finally:
        # Clean up
        comm_bus_task.cancel()
        try:
            await comm_bus_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())