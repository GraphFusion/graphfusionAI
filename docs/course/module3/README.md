# Module 3: Advanced Agent Capabilities

## Learning Objectives
By the end of this module, you will:
- Master state management techniques
- Implement sophisticated memory systems
- Integrate knowledge graphs for enhanced reasoning
- Build agents with learning capabilities

## 1. Advanced State Management

### Persistent State
```python
from graphfusionai import Agent, Role, StateManager
from typing import Dict, Any
import json

class PersistentAgent(Agent):
    def __init__(self, name: str, role: Role, state_file: str):
        super().__init__(name=name, role=role)
        self.state_file = state_file
        self.state_manager = StateManager()
        self._load_state()

    def _load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {"initialized": True}
            self._save_state()

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)

    async def update_state(self, updates: Dict[str, Any]):
        self.state.update(updates)
        self._save_state()
```

## 2. Memory Systems

### Implementing Short and Long-term Memory
```python
from graphfusionai import Memory, MemoryType
from datetime import datetime, timedelta

class MemoryAwareAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.short_term = Memory(memory_type=MemoryType.SHORT_TERM)
        self.long_term = Memory(memory_type=MemoryType.LONG_TERM)

    async def remember(self, key: str, value: Any, duration: timedelta = None):
        if duration:
            await self.short_term.store(key, value, expiry=duration)
        else:
            await self.long_term.store(key, value)

    async def recall(self, key: str) -> Any:
        # Try short-term memory first
        value = await self.short_term.retrieve(key)
        if value is not None:
            return value

        # Fall back to long-term memory
        return await self.long_term.retrieve(key)

    async def forget(self, key: str):
        await self.short_term.delete(key)
        await self.long_term.delete(key)
```

## 3. Knowledge Graph Integration

### Building a Knowledge Base
```python
from graphfusionai import KnowledgeGraph, Node, Edge, Query

class KnowledgeAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.kg = KnowledgeGraph()

    async def add_knowledge(self, subject: str, predicate: str, object: str):
        # Create nodes
        subject_node = Node(id=subject, type="entity")
        object_node = Node(id=object, type="entity")
        
        # Add nodes to graph
        self.kg.add_node(subject_node)
        self.kg.add_node(object_node)
        
        # Create relationship
        edge = Edge(
            source=subject,
            target=object,
            type=predicate
        )
        self.kg.add_edge(edge)

    async def query_knowledge(self, query: Query) -> List[Dict[str, Any]]:
        return self.kg.execute_query(query)

    async def learn_from_task(self, task: Dict[str, Any], result: Any):
        # Extract knowledge from task execution
        task_node = Node(
            id=f"task_{task['id']}",
            type="task",
            properties=task
        )
        
        result_node = Node(
            id=f"result_{task['id']}",
            type="result",
            properties={"output": result}
        )
        
        self.kg.add_node(task_node)
        self.kg.add_node(result_node)
        
        # Link task to result
        self.kg.add_edge(Edge(
            source=f"task_{task['id']}",
            target=f"result_{task['id']}",
            type="produced"
        ))
```

## 4. Learning Capabilities

### Implementing Experience-Based Learning
```python
from graphfusionai import LearningModule
import numpy as np

class AdaptiveAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.learning_module = LearningModule()
        self.experience = []

    async def learn_from_experience(self, task: Dict[str, Any], result: Any, feedback: float):
        experience = {
            "task": task,
            "result": result,
            "feedback": feedback,
            "timestamp": datetime.now()
        }
        self.experience.append(experience)
        await self.learning_module.update(experience)

    async def get_task_recommendation(self, task: Dict[str, Any]) -> Dict[str, float]:
        similar_experiences = self._find_similar_experiences(task)
        if not similar_experiences:
            return {"confidence": 0.0, "recommendation": None}

        # Calculate weighted recommendation based on similar experiences
        weights = [exp["feedback"] for exp in similar_experiences]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return {"confidence": 0.0, "recommendation": None}

        confidence = total_weight / len(similar_experiences)
        return {
            "confidence": confidence,
            "recommendation": similar_experiences[np.argmax(weights)]["result"]
        }

    def _find_similar_experiences(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implement similarity matching logic
        return [exp for exp in self.experience if self._calculate_similarity(exp["task"], task) > 0.8]

    def _calculate_similarity(self, task1: Dict[str, Any], task2: Dict[str, Any]) -> float:
        # Implement task similarity calculation
        # Return similarity score between 0 and 1
        pass
```

## Exercise: Building a Smart Assistant

Create an intelligent assistant that:
1. Maintains conversation history in short-term memory
2. Stores user preferences in long-term memory
3. Builds a knowledge graph of user interactions
4. Learns from user feedback to improve responses
5. Uses persistent state to maintain context across sessions

## Next Steps
- Review the [exercise solution](exercise_solution.py)
- Explore the [API Reference](../../api_reference.md)
- Continue to [Module 4](../module4/README.md) for multi-agent systems
