# Advanced Examples

## 1. Collaborative Research System

This example demonstrates multiple agents working together to research, analyze, and summarize information.

```python
import asyncio
from mas_framework import (
    Agent, Role, KnowledgeGraph, TaskOrchestrator,
    Message, CommunicationBus, Memory, Ontology
)

# Define roles
researcher_role = Role(
    name="researcher",
    capabilities=["research", "gather_data"],
    description="Gathers and researches information"
)

analyzer_role = Role(
    name="analyzer",
    capabilities=["analyze", "process_data"],
    description="Analyzes and processes research data"
)

summarizer_role = Role(
    name="summarizer",
    capabilities=["summarize", "generate_report"],
    description="Creates summaries and reports"
)

# Define agents
class ResearchAgent(Agent):
    async def _process_task(self, task):
        if task["type"] == "research":
            # Simulate research process
            research_data = {
                "topic": task["data"]["topic"],
                "findings": f"Research findings for {task['data']['topic']}",
                "sources": ["source1", "source2"]
            }
            self.remember("research_data", research_data)
            return {"status": "success", "data": research_data}
        return None

class AnalyzerAgent(Agent):
    async def _process_task(self, task):
        if task["type"] == "analyze":
            research_data = task["data"]["research_data"]
            analysis = {
                "key_points": ["point1", "point2"],
                "metrics": {"relevance": 0.8, "confidence": 0.9}
            }
            return {"status": "success", "analysis": analysis}
        return None

class SummarizerAgent(Agent):
    async def _process_task(self, task):
        if task["type"] == "summarize":
            analysis = task["data"]["analysis"]
            summary = {
                "title": "Research Summary",
                "overview": "Brief overview of findings",
                "conclusions": ["conclusion1", "conclusion2"]
            }
            return {"status": "success", "summary": summary}
        return None

async def main():
    # Initialize components
    kg = KnowledgeGraph()
    memory = Memory()
    orchestrator = TaskOrchestrator()
    comm_bus = CommunicationBus()

    # Create agents
    researcher = ResearchAgent(name="Researcher1", role=researcher_role)
    analyzer = AnalyzerAgent(name="Analyzer1", role=analyzer_role)
    summarizer = SummarizerAgent(name="Summarizer1", role=summarizer_role)

    # Set up knowledge graph with ontology
    ontology = Ontology()
    
    research_class = OntologyClass(
        name="Research",
        properties={
            "topic": "string",
            "findings": "string",
            "sources": "list"
        }
    )
    
    analysis_class = OntologyClass(
        name="Analysis",
        properties={
            "key_points": "list",
            "metrics": "dict"
        }
    )
    
    ontology.add_class(research_class)
    ontology.add_class(analysis_class)

    # Create and execute workflow
    try:
        # Research task
        research_task = {
            "id": "task1",
            "type": "research",
            "data": {"topic": "AI Knowledge Graphs"}
        }
        research_result = await orchestrator.execute_task(researcher, research_task)
        
        # Analysis task
        analysis_task = {
            "id": "task2",
            "type": "analyze",
            "data": {"research_data": research_result["data"]}
        }
        analysis_result = await orchestrator.execute_task(analyzer, analysis_task)
        
        # Summary task
        summary_task = {
            "id": "task3",
            "type": "summarize",
            "data": {"analysis": analysis_result["analysis"]}
        }
        summary_result = await orchestrator.execute_task(summarizer, summary_task)

        # Store results in knowledge graph
        kg.add_node(Node(
            id="research_1",
            type="Research",
            properties=research_result["data"]
        ))
        
        kg.add_node(Node(
            id="analysis_1",
            type="Analysis",
            properties=analysis_result["analysis"]
        ))
        
        kg.add_edge(Edge(
            source="research_1",
            target="analysis_1",
            type="analyzed_by"
        ))

        print("Workflow completed successfully!")
        print("Summary:", summary_result["summary"])

    except Exception as e:
        print(f"Error in workflow: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 2. Knowledge Graph-Based Agent Collaboration

This example shows how agents can use the knowledge graph to share and build upon each other's knowledge.

```python
from mas_framework import KnowledgeGraph, Node, Edge, Agent, Role

# Define knowledge-aware agent
class KnowledgeAwareAgent(Agent):
    def __init__(self, name: str, role: Role, knowledge_graph: KnowledgeGraph):
        super().__init__(name=name, role=role)
        self.kg = knowledge_graph

    async def _process_task(self, task):
        if task["type"] == "query_knowledge":
            # Query knowledge graph for relevant information
            results = self.kg.query(node_type=task["data"]["type"])
            
            # Process and analyze results
            processed_results = self._analyze_results(results)
            
            # Add new knowledge based on analysis
            new_knowledge = Node(
                id=f"knowledge_{task['id']}",
                type="Insight",
                properties={"findings": processed_results}
            )
            self.kg.add_node(new_knowledge)
            
            return {
                "status": "success",
                "results": processed_results,
                "new_knowledge_id": new_knowledge.id
            }
        return None

    def _analyze_results(self, results):
        # Implementation of result analysis
        return {
            "insights": "Derived insights from knowledge graph",
            "confidence": 0.85
        }

# Usage example
async def knowledge_collaboration_example():
    kg = KnowledgeGraph()
    
    # Initialize knowledge graph with some data
    kg.add_node(Node(
        id="concept_1",
        type="Concept",
        properties={"name": "AI", "description": "Artificial Intelligence"}
    ))
    
    # Create knowledge-aware agents
    agent1 = KnowledgeAwareAgent(
        name="KnowledgeAgent1",
        role=Role(
            name="knowledge_processor",
            capabilities=["query_knowledge"],
            description="Processes and extends knowledge"
        ),
        knowledge_graph=kg
    )
    
    # Query and extend knowledge
    task = {
        "id": "task_1",
        "type": "query_knowledge",
        "data": {"type": "Concept"}
    }
    
    result = await agent1.handle_task(task)
    print("Task result:", result)
```

## 3. Advanced Memory Management

Example demonstrating sophisticated memory management with context awareness.

```python
from mas_framework import Memory, KnowledgeGraph, Node, Edge

class ContextAwareMemory(Memory):
    def __init__(self):
        super().__init__()
        self.context_history = []

    def store_with_context(self, key: str, value: Any, context: Dict[str, Any]):
        # Store main memory entry
        self.store(key, value, context)
        
        # Track context history
        self.context_history.append({
            "timestamp": datetime.now(),
            "key": key,
            "context": context
        })
        
        # Create context relationships in knowledge graph
        context_node = Node(
            id=f"context_{len(self.context_history)}",
            type="Context",
            properties=context
        )
        self.kg.add_node(context_node)
        
        # Link memory to context
        self.kg.add_edge(Edge(
            source=key,
            target=context_node.id,
            type="has_context"
        ))

    def retrieve_with_history(self, key: str) -> Dict[str, Any]:
        # Get current value
        current = self.retrieve(key)
        
        # Get context history
        history = [
            entry for entry in self.context_history
            if entry["key"] == key
        ]
        
        return {
            "current": current,
            "history": history
        }

# Usage example
memory = ContextAwareMemory()

# Store with context
memory.store_with_context(
    key="user_preference",
    value={"theme": "dark"},
    context={
        "user_id": "user_123",
        "session_id": "session_456",
        "timestamp": datetime.now()
    }
)

# Retrieve with history
result = memory.retrieve_with_history("user_preference")
print("Memory retrieval:", result)
```

These examples demonstrate advanced usage of the framework's features including:
- Multi-agent collaboration
- Knowledge graph integration
- Context-aware memory management
- Task orchestration
- Ontology-based validation

For more examples and use cases, check the [examples](../examples/) directory in the repository.
