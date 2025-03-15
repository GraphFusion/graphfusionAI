![graph-fusion-logo](https://github.com/user-attachments/assets/de5a4a09-a7e4-4b21-b3ec-01d5a3097ecd) 
 
</p>
<h1 align="center" weight='300'>GraphFusionAI: The Graph-Based AI Agent Framework</h1>
<div align="center">

  [![GitHub release](https://img.shields.io/badge/Github-Release-blue)](https://github.com/GraphFusion/GraphFusion-NMN/releases)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/GraphFusion/graphfusionAI/blob/main/LICENSE)
  [![Join us on Teams](https://img.shields.io/badge/Join-Teams-blue)](https://teams.microsoft.com/)
  [![Discord Server](https://img.shields.io/badge/Discord-Server-blue)](https://discord.gg/zK94WvRjZT)

</div>
<h3 align="center">
   <a href="https://github.com/GraphFusion/graphfusionAI/tree/main/docs"><b>Docs</b></a> &bull;
   <a href="https://graphfusion.github.io/graphfusion.io/"><b>Website</b></a>
</h3> 
<br />

⚠️ **This project is in early development!** Expect bugs, incomplete features, and potential breaking changes. If you're contributing, **please read the codebase carefully** and help us improve it.

GraphFusionAI is a Python framework for building multi-agent systems where AI agents collaborate to complete tasks. The framework provides a structured way to define, manage, and coordinate multiple agents, each with specific roles, abilities, and goals.

## Key Features

- **Multi-Agent Architecture**: Build systems with multiple collaborative AI agents
- **Knowledge Graph Integration**: Enhanced data understanding with spaCy-powered entity extraction
- **Task Orchestration**: Structured task distribution and execution with async support
- **Memory Management**: Vector-based persistent storage and retrieval
- **LLM Integration**: Built-in support for language models
- **Tool Framework**: Extensible tool system with validation and async support
- **Communication Bus**: Asynchronous inter-agent messaging system
- **Enhanced Inference**: Pattern-based relationship inference in knowledge graphs

## Installation

```bash
!pip install graphfusionai
!python -m spacy download en_core_web_sm
```

## Quick Start

First, install the required dependencies and language model:

```bash
pip install graphfusionai
python -m spacy download en_core_web_sm
```

Here's a simple example of creating a multi-agent system:

```python
import asyncio
from graphfusionai import (
    Agent, Role, KnowledgeGraph, TaskOrchestrator,
    Message, CommunicationBus, Memory
)
from graphfusionai.task_orchestrator import Task
from rich.console import Console

# Initialize console for nice output
console = Console()

# Define roles
researcher_role = Role(
    name="researcher",
    capabilities=["research", "analyze"],
    description="Performs research and analysis tasks"
)

# Create an agent class
class ResearchAgent(Agent):
    async def _process_task(self, task: dict) -> dict:
        if task["type"] == "research":
            # Use the knowledge graph for enhanced understanding
            self.kg.extract_knowledge_from_text(task["data"]["content"])
            return {"research_results": f"Research completed for {task['data']['topic']}"}
        return None

async def main():
    # Initialize components
    kg = KnowledgeGraph()
    orchestrator = TaskOrchestrator()
    comm_bus = CommunicationBus()
    
    # Create agent instance
    researcher = ResearchAgent(
        name="ResearchAgent1",
        role=researcher_role
    )
    
    # Create a task
    research_task = Task(
        id="task1",
        type="research",
        data={
            "topic": "AI Knowledge Graphs",
            "content": "Researching the integration of AI with knowledge graphs."
        },
        assigned_to=researcher.id
    )
    
    # Add task to orchestrator
    orchestrator.add_task(research_task)
    
    # Start communication bus
    comm_bus_task = asyncio.create_task(comm_bus.start())
    
    try:
        # Execute task
        result = await orchestrator.execute_task(researcher, research_task)
        console.print("[green]Research task completed:", result)
    finally:
        # Clean up
        comm_bus_task.cancel()
        try:
            await comm_bus_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
```

Save this code as `simple_example.py` and run it with:

```bash
python simple_example.py
```

For more examples, check out our [examples directory on GitHub](https://github.com/GraphFusion/graphfusionAI/tree/main/examples).

## Example Workflows

GraphFusionAI includes several example workflows demonstrating different features:

- `simple_workflow.py`: Basic agent interaction and task processing
- `agent_examples.py`: Different types of specialized agents
- `llm_agent_example.py`: Language model integration
- `advanced_orchestration_example.py`: Complex task management
- `enhanced_memory_example.py`: Vector-based memory operations
- `tool_framework_example.py`: Custom tool creation and usage
- `advanced_knowledge_graph_example.py`: Knowledge graph capabilities
- `team_collaboration_example.py`: Multi-agent collaboration patterns

## Documentation

- [Getting Started](https://github.com/GraphFusion/graphfusionAI/blob/main/docs/getting_started.md): Quick start guide and basic concepts
- [Core Concepts](https://github.com/GraphFusion/graphfusionAI/blob/main/docs/core_concepts.md): Framework architecture and components
- [API Reference](https://github.com/GraphFusion/graphfusionAI/blob/main/docs/api_reference.md): Detailed API documentation
- [Advanced Examples](https://github.com/GraphFusion/graphfusionAI/blob/main/docs/advanced_examples.md): Complex usage patterns
- [Agent Development Guide](https://github.com/GraphFusion/graphfusionAI/blob/main/docs/agent_development_guide.md): Creating custom agents
- [Dependencies](https://github.com/GraphFusion/graphfusionAI/blob/main/docs/dependencies.md): Framework requirements and versions
