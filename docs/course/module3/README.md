# Module 3: Advanced Agent Capabilities

## Learning Objectives
By the end of this module, you will:
- Master agent state management
- Implement sophisticated memory systems
- Integrate knowledge graphs
- Build agents with learning capabilities

## 1. State Management

Agent state represents the current condition and context of an agent. It's crucial for:
- Tracking progress
- Maintaining configuration
- Managing resources
- Handling dependencies

### Implementation Example

```python
from graphfusionai import Agent, Role, State
from typing import Dict, Any
from datetime import datetime

class StateAwareAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.state = State({
            "status": "idle",
            "last_active": None,
            "task_count": 0,
            "resources": {},
            "configuration": {}
        })

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Update state before processing
        self.state.update({
            "status": "processing",
            "last_active": datetime.now().isoformat(),
            "task_count": self.state.get("task_count", 0) + 1
        })

        try:
            result = await self._execute_task(task)
            
            # Update state after successful processing
            self.state.update({
                "status": "idle",
                "last_result": result
            })
            
            return result
            
        except Exception as e:
            # Update state to reflect error
            self.state.update({
                "status": "error",
                "last_error": str(e)
            })
            raise

    def get_status(self) -> Dict[str, Any]:
        return self.state.to_dict()
```

## 2. Memory Systems

Memory systems allow agents to:
- Store and retrieve information
- Learn from experience
- Make informed decisions
- Share knowledge

### Types of Memory

1. **Short-term Memory**
   - Temporary storage
   - Recent events and context
   - Limited capacity

2. **Long-term Memory**
   - Persistent storage
   - Learning and experience
   - Pattern recognition

3. **Working Memory**
   - Active processing
   - Current task context
   - Decision making

### Implementation Example

```python
from graphfusionai import Agent, Role, Memory
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta

class MemoryAwareAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        
        # Initialize different memory types
        self.short_term = Memory(max_size=100, ttl=timedelta(minutes=30))
        self.long_term = Memory(persistence_path="agent_memory.json")
        self.working = Memory(max_size=10)

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Store task in short-term memory
        self.short_term.store(
            key=f"task_{datetime.now().isoformat()}",
            value=task
        )

        # Check if we've seen similar tasks
        similar_tasks = self._find_similar_tasks(task)
        if similar_tasks:
            # Use previous experience
            self.working.store("reference_tasks", similar_tasks)

        result = await self._execute_task(task)

        # Learn from experience
        self._store_experience(task, result)
        
        return result

    def _find_similar_tasks(self, task: Dict[str, Any]) -> list:
        similar = []
        for key, stored_task in self.long_term.items():
            if self._calculate_similarity(task, stored_task) > 0.8:
                similar.append(stored_task)
        return similar

    def _store_experience(self, task: Dict[str, Any], result: Any) -> None:
        # Store in long-term memory
        self.long_term.store(
            key=f"experience_{datetime.now().isoformat()}",
            value={
                "task": task,
                "result": result,
                "context": self.working.get_all()
            }
        )

    def _calculate_similarity(self, task1: Dict[str, Any], 
                            task2: Dict[str, Any]) -> float:
        # Implement similarity calculation
        # This is a simplified example
        return sum(1 for k, v in task1.items() 
                  if k in task2 and task2[k] == v) / len(task1)

    def get_experience(self, task_type: str) -> list:
        return [
            exp for exp in self.long_term.values()
            if exp["task"].get("type") == task_type
        ]
```

## 3. Knowledge Graph Integration

Knowledge graphs enable agents to:
- Represent complex relationships
- Reason about entities and connections
- Share structured knowledge
- Make inferences

### Implementation Example

```python
from graphfusionai import Agent, Role, KnowledgeGraph
from graphfusionai.knowledge import Node, Edge, Query
from typing import Dict, Any

class KnowledgeAwareAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.knowledge = KnowledgeGraph()

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Add task to knowledge graph
        task_node = Node(
            id=f"task_{task['id']}",
            type="Task",
            properties=task
        )
        self.knowledge.add_node(task_node)

        # Find related knowledge
        related = self.knowledge.query(Query()
            .match(type="Task")
            .where(lambda x: x.properties["type"] == task["type"])
            .limit(5)
        )

        # Process task using related knowledge
        result = await self._execute_with_knowledge(task, related)

        # Store result in knowledge graph
        result_node = Node(
            id=f"result_{task['id']}",
            type="Result",
            properties=result
        )
        self.knowledge.add_node(result_node)

        # Link task to result
        self.knowledge.add_edge(Edge(
            source=task_node.id,
            target=result_node.id,
            type="produced"
        ))

        return result

    async def _execute_with_knowledge(self, task: Dict[str, Any], 
                                    related: list) -> Any:
        # Use related knowledge to enhance task execution
        enhanced_task = self._enhance_task(task, related)
        return await self._execute_task(enhanced_task)

    def _enhance_task(self, task: Dict[str, Any], 
                     related: list) -> Dict[str, Any]:
        # Enhance task with related knowledge
        enhanced = task.copy()
        
        # Add insights from related tasks
        insights = []
        for node in related:
            if node.properties.get("success", False):
                insights.append({
                    "source": node.id,
                    "strategy": node.properties.get("strategy"),
                    "outcome": node.properties.get("outcome")
                })
        
        enhanced["insights"] = insights
        return enhanced
```

## Exercise: Build a Learning Agent

Create an agent that:
1. Uses all three memory types
2. Maintains state across tasks
3. Builds a knowledge graph of experiences
4. Improves performance based on past experiences

## Solution
Check the [exercise solution](exercise_solution.py) for a complete implementation.

## Next Steps
- Review the [API Reference](../../api_reference.md)
- Explore the [example notebooks](../../examples/)
- Move on to [Module 4](../module4/README.md) to learn about multi-agent systems
