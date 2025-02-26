   
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

A Python framework for building multi-agent systems where multiple AI agents collaborate to complete tasks. The framework provides a structured way to define, manage, and coordinate multiple agents, each with specific roles, abilities, and goals.

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
pip install graphfusionai
```

## Quick Start

Here's a simple example of creating a multi-agent system:

```python
from mas_framework import Agent, Role, Tool, KnowledgeGraph, TaskOrchestrator

# Define a tool
@Tool.create(
    name="calculate",
    description="Performs calculations"
)
def calculate(x: int, y: int) -> int:
    return x + y

# Define roles
researcher_role = Role(
    name="researcher",
    capabilities=["research", "analyze"],
    description="Performs research and analysis tasks"
)

# Create agents
class ResearchAgent(Agent):
    async def _process_task(self, task):
        if task["type"] == "research":
            # Use the knowledge graph for enhanced understanding
            self.kg.extract_knowledge_from_text(task["data"]["content"])
            return {"research_results": f"Research completed for {task['data']['topic']}"}
        
        return None

# Initialize components
kg = KnowledgeGraph()
orchestrator = TaskOrchestrator()

# Create and use agents
researcher = ResearchAgent(
    name="ResearchAgent1",
    role=researcher_role
)

# Execute tasks
task = {
    "id": "task1",
    "type": "research",
    "data": {
        "topic": "AI Knowledge Graphs",
        "content": "Researching the integration of AI with knowledge graphs."
    }
}
result = await orchestrator.execute_task(researcher, task)
```

## Example Workflows

The framework includes several example workflows demonstrating different features:

- `simple_workflow.py`: Basic agent interaction and task processing
- `agent_examples.py`: Different types of specialized agents
- `llm_agent_example.py`: Language model integration
- `advanced_orchestration_example.py`: Complex task management
- `enhanced_memory_example.py`: Vector-based memory operations
- `tool_framework_example.py`: Custom tool creation and usage
- `advanced_knowledge_graph_example.py`: Knowledge graph capabilities
- `team_collaboration_example.py`: Multi-agent collaboration patterns

## Documentation

- [Getting Started](getting_started.md): Quick start guide and basic concepts
- [Core Concepts](core_concepts.md): Framework architecture and components
- [API Reference](api_reference.md): Detailed API documentation
- [Advanced Examples](advanced_examples.md): Complex usage patterns
- [Agent Development Guide](agent_development_guide.md): Creating custom agents
- [Dependencies](dependencies.md): Framework requirements and versions
