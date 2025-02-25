# Building Agents with MAS Framework

This guide walks you through the process of creating custom agents using the MAS Framework. We'll cover everything from basic agent creation to advanced features like knowledge graph integration and inter-agent communication.

## Basic Agent Creation

### 1. Define Agent Role

First, define your agent's role and capabilities:

```python
from mas_framework import Role, Agent

custom_role = Role(
    name="data_processor",
    capabilities=["process_data", "analyze_trends"],
    description="Processes and analyzes data streams"
)
```

### 2. Create Custom Agent

Implement your agent by subclassing the base Agent class:

```python
class DataProcessorAgent(Agent):
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        if task["type"] == "process_data":
            # Implement data processing logic
            return {
                "processed_data": f"Processed {task['data']['input']}"
            }
        elif task["type"] == "analyze_trends":
            # Implement trend analysis logic
            return {
                "trends": f"Analysis for {task['data']['dataset']}"
            }
        raise ValueError(f"Unsupported task type: {task['type']}")
```

### 3. State Management

Agents can maintain internal state:

```python
# Update agent state
agent.update_state({
    "last_processed_file": "data.csv",
    "processing_status": "completed"
})

# Store information in agent's memory
agent.remember("analysis_results", results)
```

## Knowledge Graph Integration

### 1. Storing Knowledge

Integrate your agent with the Knowledge Graph:

```python
from mas_framework import KnowledgeGraph, Node, Edge

class KnowledgeAwareAgent(Agent):
    def __init__(self, **data):
        super().__init__(**data)
        self.kg = KnowledgeGraph()

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Store task-related information in Knowledge Graph
        task_node = Node(
            id=task["id"],
            type="task",
            properties=task
        )
        self.kg.add_node(task_node)
        
        # Process task and store results
        result = await self._execute_task_logic(task)
        
        result_node = Node(
            id=f"result_{task['id']}",
            type="result",
            properties=result
        )
        self.kg.add_node(result_node)
        
        # Link task to result
        edge = Edge(
            source=task["id"],
            target=f"result_{task['id']}",
            type="has_result"
        )
        self.kg.add_edge(edge)
        
        return result
```

## Inter-Agent Communication

### 1. Setting Up Communication

Enable communication between agents:

```python
from mas_framework import CommunicationBus, Message

async def handle_message(message: Message):
    print(f"Received message: {message.content}")

# Subscribe agent to communication bus
comm_bus = CommunicationBus()
await comm_bus.subscribe(agent.id, handle_message)

# Send message to another agent
message = Message(
    id="msg_1",
    sender=agent.id,
    receiver=other_agent.id,
    content={"type": "request", "data": "process_this"},
    type="task_request"
)
await comm_bus.send_message(message)
```

## Complete Example

Here's a complete example of a sophisticated agent that uses multiple framework features:

```python
from mas_framework import (
    Agent, Role, KnowledgeGraph, Message,
    Node, Edge, Memory
)

class AnalyticsAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.kg = KnowledgeGraph()
        self.memory = Memory()

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Store task in knowledge graph
        self._store_task_in_kg(task)
        
        # Process based on task type
        if task["type"] == "analyze":
            result = await self._analyze_data(task["data"])
            
            # Store result in memory with context
            self.memory.store(
                key=f"analysis_{task['id']}", 
                value=result,
                context={"task_id": task["id"], "timestamp": datetime.now()}
            )
            
            # Update knowledge graph
            self._store_result_in_kg(task["id"], result)
            
            return result
            
        raise ValueError(f"Unsupported task type: {task['type']}")
    
    def _store_task_in_kg(self, task: Dict[str, Any]):
        node = Node(
            id=task["id"],
            type="task",
            properties=task
        )
        self.kg.add_node(node)
    
    def _store_result_in_kg(self, task_id: str, result: Dict[str, Any]):
        node = Node(
            id=f"result_{task_id}",
            type="result",
            properties=result
        )
        self.kg.add_node(node)
        
        edge = Edge(
            source=task_id,
            target=f"result_{task_id}",
            type="has_result"
        )
        self.kg.add_edge(edge)

# Usage
analytics_role = Role(
    name="analytics",
    capabilities=["analyze"],
    description="Performs data analysis"
)

agent = AnalyticsAgent(
    name="AnalyticsAgent1",
    role=analytics_role
)
```

## Best Practices

1. **Task Handling**
   - Implement clear error handling in `_process_task`
   - Validate task types against role capabilities
   - Return structured results

2. **Knowledge Management**
   - Use the Knowledge Graph for relational data
   - Store important information in agent memory
   - Maintain relevant state

3. **Communication**
   - Handle messages asynchronously
   - Validate message content
   - Implement timeout handling

## Common Patterns

### 1. Chain of Responsibility

```python
class ChainAgent(Agent):
    def __init__(self, **data):
        super().__init__(**data)
        self.next_agent_id = None

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        if self._can_handle(task):
            return await self._handle_task(task)
        elif self.next_agent_id:
            # Forward to next agent
            message = Message(
                id=str(uuid4()),
                sender=self.id,
                receiver=self.next_agent_id,
                content=task,
                type="task_forward"
            )
            await self.comm_bus.send_message(message)
            return {"status": "forwarded", "to": self.next_agent_id}
```

### 2. Observer Pattern

```python
class ObserverAgent(Agent):
    async def handle_message(self, message: Message):
        if message.type == "status_update":
            # Update internal state based on observed changes
            self.update_state({
                "last_update": message.content,
                "timestamp": datetime.now()
            })
```

### 3. State Machine

```python
class StatefulAgent(Agent):
    def __init__(self, **data):
        super().__init__(**data)
        self.state_machine = {
            "idle": ["processing"],
            "processing": ["completed", "error"],
            "completed": ["idle"],
            "error": ["idle"]
        }
        self.current_state = "idle"

    def transition_to(self, new_state: str):
        if new_state in self.state_machine[self.current_state]:
            self.current_state = new_state
            self.update_state({"status": new_state})
        else:
            raise ValueError(f"Invalid state transition: {self.current_state} -> {new_state}")
```

## Testing Agents

Here's how to test your custom agents:

```python
import pytest
from mas_framework import TaskOrchestrator

@pytest.mark.asyncio
async def test_analytics_agent():
    # Create agent
    agent = AnalyticsAgent(
        name="TestAgent",
        role=analytics_role
    )
    
    # Create task
    task = {
        "id": "test_1",
        "type": "analyze",
        "data": {"dataset": "test_data"}
    }
    
    # Execute task
    orchestrator = TaskOrchestrator()
    result = await orchestrator.execute_task(agent, task)
    
    # Verify result
    assert result["status"] == "success"
    assert "analysis" in result["result"]
```
