# Multi-Agent System Framework with Knowledge Graph Integration

A Python framework for building multi-agent systems where multiple AI agents collaborate to complete tasks. The framework provides a structured way to define, manage, and coordinate multiple agents, each with specific roles, abilities, and goals.

## Key Features

- **Multi-Agent Architecture**: Build systems with multiple collaborative AI agents
- **Knowledge Graph Integration**: Enhanced data understanding and agent collaboration
- **Task Orchestration**: Structured task distribution and execution
- **Memory Management**: Persistent storage and retrieval of agent knowledge
- **Flexible Communication**: Inter-agent messaging system
- **Ontology Support**: Define and manage domain-specific knowledge structures

## Installation

```bash
pip install mas-framework
```

## Quick Start

Here's a simple example of creating a multi-agent system:

```python
from mas_framework import Agent, Role, KnowledgeGraph, TaskOrchestrator

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
            return {"research_results": f"Research completed for {task['data']['topic']}"}
        elif task["type"] == "analyze":
            return {"analysis_results": f"Analysis completed for {task['data']['subject']}"}

# Initialize components
kg = KnowledgeGraph()
orchestrator = TaskOrchestrator()

# Create and use agents
researcher = ResearchAgent(
    name="ResearchAgent1",
    role=researcher_role
)

# Execute tasks
result = await orchestrator.execute_task(researcher, task)
```

## Documentation Structure

- [API Reference](api_reference.md): Detailed documentation of all classes and methods
- [Examples](examples.md): More detailed examples and use cases
- [Knowledge Graph Guide](knowledge_graph.md): Detailed guide on Knowledge Graph integration
- [Advanced Usage](advanced_usage.md): Advanced features and customization options
