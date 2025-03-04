# Module 1: Foundations of Agent Development

## Learning Objectives
By the end of this module, you will:
- Understand what agents are and their key characteristics
- Know the core components of the GraphFusionAI framework
- Have a working development environment
- Be able to create a basic agent template

## 1. What is an Agent?

An agent is an autonomous software entity that:
- Perceives its environment through sensors
- Makes decisions based on its knowledge and goals
- Takes actions to achieve those goals
- Learns from its experiences

### Key Characteristics
- **Autonomy**: Acts independently
- **Reactivity**: Responds to environment changes
- **Proactivity**: Takes initiative to achieve goals
- **Social Ability**: Interacts with other agents

## 2. GraphFusionAI Framework Overview

The GraphFusionAI framework provides:
```python
from graphfusionai import Agent, Role, KnowledgeGraph

# Core Components:
# 1. Agent - Base class for all agents
# 2. Role - Defines agent capabilities
# 3. KnowledgeGraph - Stores and manages agent knowledge
# 4. Memory - Manages agent's memory system
# 5. CommunicationBus - Enables inter-agent communication
```

## 3. Setting Up Your Environment

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install GraphFusionAI:
```bash
pip install graphfusionai
```

3. Verify installation:
```python
import graphfusionai
print(graphfusionai.__version__)
```

## 4. Your First Agent Template

Create a file named `my_first_agent.py`:

```python
from graphfusionai import Agent, Role
from typing import Dict, Any

# Define the agent's role
basic_role = Role(
    name="hello_agent",
    capabilities=["greet"],
    description="A simple greeting agent"
)

# Create your first agent
class HelloAgent(Agent):
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        if task["type"] == "greet":
            return f"Hello, {task['data'].get('name', 'World')}!"
        raise ValueError(f"Unsupported task type: {task['type']}")

# Test your agent
async def main():
    agent = HelloAgent(name="Greeter", role=basic_role)
    result = await agent.process_task({
        "type": "greet",
        "data": {"name": "Alice"}
    })
    print(result)  # Output: Hello, Alice!

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Exercise
1. Create the HelloAgent as shown above
2. Modify it to support a new capability: "farewell"
3. Add error handling for invalid inputs

## Next Steps
- Review the [exercise solution](exercise_solution.py)
- Move on to [Module 2](../module2/README.md) when ready
- Explore the [API Reference](../../api_reference.md) for more details
