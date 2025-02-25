# Getting Started with MAS Framework

## Introduction
The MAS Framework is a Python library for building multi-agent systems with Knowledge Graph integration. It provides a structured way to define, manage, and coordinate multiple AI agents, each with specific roles, abilities, and goals.

## Key Features
- Multi-agent coordination and communication
- Knowledge Graph integration for enhanced data understanding
- Task orchestration and workflow management
- Memory management for agents
- Ontology-based knowledge representation

## Installation
```bash
pip install mas-framework
```

## Quick Start
Here's a simple example of creating and running a multi-agent system:

```python
from mas_framework import Agent, Role, TaskOrchestrator, KnowledgeGraph, Memory

# Define agent roles
research_role = Role(
    name="researcher",
    capabilities=["research", "analyze"],
    description="Performs research and analysis tasks"
)

# Create agents
class ResearchAgent(Agent):
    async def _process_task(self, task):
        if task["type"] == "research":
            return {"research_results": f"Research completed for {task['data']['topic']}"}
        return None

# Initialize components
kg = KnowledgeGraph()
memory = Memory()
orchestrator = TaskOrchestrator()

# Create and run tasks
researcher = ResearchAgent(name="Researcher1", role=research_role)
task = {
    "id": "task1",
    "type": "research",
    "data": {"topic": "AI Knowledge Graphs"}
}

# Execute task
result = await orchestrator.execute_task(researcher, task)
```

## Core Components

### 1. Agents
Agents are the primary actors in the system. Each agent:
- Has a specific role with defined capabilities
- Can process tasks
- Maintains its own memory
- Communicates with other agents

### 2. Knowledge Graph
The Knowledge Graph component:
- Stores interconnected data
- Enables semantic understanding
- Facilitates agent collaboration
- Provides context for decision-making

### 3. Task Orchestrator
The Task Orchestrator:
- Manages task distribution
- Coordinates agent activities
- Tracks task status
- Handles task dependencies

### 4. Memory
The Memory system:
- Stores agent experiences
- Maintains context
- Enables knowledge persistence
- Supports decision-making

## Next Steps
- Explore the [Advanced Examples](advanced_examples.md)
- Read about [Core Concepts](core_concepts.md)
- Check the [API Reference](api_reference.md)
