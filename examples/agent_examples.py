"""
This module contains example implementations of different agent types
using the MAS Framework.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from uuid import uuid4
import json
from graphfusionai import (
    Agent, Role, KnowledgeGraph, TaskOrchestrator,
    Message, CommunicationBus, Memory, Ontology,
    Node, Edge, Tool
)
from graphfusionai.ontology import OntologyClass, Relationship

# Add custom node and edge types
KnowledgeGraph.ALLOWED_NODE_TYPES.add("workflow")
KnowledgeGraph.ALLOWED_NODE_TYPES.add("workflow_step")
KnowledgeGraph.ALLOWED_EDGE_TYPES.add("workflow_step")

# Task Implementations
async def collect_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Collect data from a source"""
    return {
        "timestamp": datetime.now().isoformat(),
        "source": data["source"],
        "values": [1, 2, 3, 4, 5]  # Example data
    }

async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process collected data"""
    values = data["values"]
    return {
        "mean": sum(values) / len(values),
        "max": max(values),
        "min": min(values)
    }

async def analyze_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze processed data"""
    return {
        "insights": [
            f"Average value: {data['mean']}",
            f"Range: {data['max'] - data['min']}"
        ]
    }

# Data Collection Agent
class DataCollectorAgent(Agent):
    """Agent responsible for collecting and validating data"""
    def __init__(self, **data):
        super().__init__(**data)
        self.register_tool(Tool(
            name="collect",
            description="Collect data from a source",
            func=collect_data,
            async_handler=True
        ))

# Data Processing Agent
class DataProcessorAgent(Agent):
    """Agent responsible for processing collected data"""
    def __init__(self, **data):
        super().__init__(**data)
        self.register_tool(Tool(
            name="process",
            description="Process collected data",
            func=process_data,
            async_handler=True
        ))

# Analysis Agent
class AnalysisAgent(Agent):
    """Agent responsible for analyzing processed data"""
    def __init__(self, **data):
        super().__init__(**data)
        self.register_tool(Tool(
            name="analyze",
            description="Analyze processed data",
            func=analyze_data,
            async_handler=True
        ))

# Coordinator Agent
class CoordinatorAgent(Agent):
    """Agent responsible for coordinating other agents"""

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize components as instance variables
        self._kg = KnowledgeGraph()
        self._memory = Memory()
        self._orchestrator = TaskOrchestrator()
        self._registered_agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        """Register an agent for coordination"""
        self._registered_agents[agent.role.name] = agent

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        if task["type"] == "coordinate":
            workflow_id = str(uuid4())
            results = []

            try:
                # 1. Collect Data
                collector = self._registered_agents["collector"]
                collect_task = {
                    "id": f"{workflow_id}_collect",
                    "type": "collect",
                    "data": {"source": task["data"]["source"]}
                }
                collect_result = await collector.handle_task(collect_task)
                if collect_result["status"] == "success":
                    collect_result["result"] = collect_result["result"]["result"]
                results.append(("collect", collect_result))

                # 2. Process Data
                if collect_result["status"] == "success":
                    processor = self._registered_agents["processor"]
                    process_task = {
                        "id": f"{workflow_id}_process",
                        "type": "process",
                        "data": collect_result["result"]
                    }
                    process_result = await processor.handle_task(process_task)
                    if process_result["status"] == "success":
                        process_result["result"] = process_result["result"]["result"]
                    results.append(("process", process_result))

                    # 3. Analyze Data
                    if process_result["status"] == "success":
                        analyzer = self._registered_agents["analyzer"]
                        analyze_task = {
                            "id": f"{workflow_id}_analyze",
                            "type": "analyze",
                            "data": process_result["result"]
                        }
                        analyze_result = await analyzer.handle_task(analyze_task)
                        if analyze_result["status"] == "success":
                            analyze_result["result"] = analyze_result["result"]["result"]
                        results.append(("analyze", analyze_result))

                # Store workflow results in knowledge graph
                self._store_workflow_results(workflow_id, results)

                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "results": results
                }

            except Exception as e:
                return {
                    "status": "error",
                    "workflow_id": workflow_id,
                    "error": str(e),
                    "partial_results": results
                }

    def _store_workflow_results(self, workflow_id: str, results: List[tuple]):
        """Store workflow results in knowledge graph"""
        workflow_node = Node(
            id=workflow_id,
            type="workflow",
            properties={"timestamp": datetime.now().isoformat()}
        )
        self._kg.add_node(workflow_node)

        for step, result in results:
            result_node = Node(
                id=f"{workflow_id}_{step}",
                type="workflow_step",
                properties={
                    "step": step,
                    "result": result
                }
            )
            self._kg.add_node(result_node)

            edge = Edge(
                source=workflow_id,
                target=f"{workflow_id}_{step}",
                type="workflow_step"
            )
            self._kg.add_edge(edge)

async def main():
    # Create roles
    collector_role = Role(
        name="collector",
        capabilities=["collect"],
        description="Collects data from sources"
    )

    processor_role = Role(
        name="processor",
        capabilities=["process"],
        description="Processes collected data"
    )

    analyzer_role = Role(
        name="analyzer",
        capabilities=["analyze"],
        description="Analyzes processed data"
    )

    coordinator_role = Role(
        name="coordinator",
        capabilities=["coordinate"],
        description="Coordinates data workflow"
    )

    # Create agents
    collector = DataCollectorAgent(
        name="DataCollector1",
        role=collector_role
    )

    processor = DataProcessorAgent(
        name="DataProcessor1",
        role=processor_role
    )

    analyzer = AnalysisAgent(
        name="Analyzer1",
        role=analyzer_role
    )

    coordinator = CoordinatorAgent(
        name="Coordinator1",
        role=coordinator_role
    )

    # Register agents with coordinator
    coordinator.register_agent(collector)
    coordinator.register_agent(processor)
    coordinator.register_agent(analyzer)

    # Create coordination task
    task = {
        "id": "task1",
        "type": "coordinate",
        "data": {
            "source": "sensor_1"
        }
    }

    # Execute workflow
    result = await coordinator._process_task(task)
    print("\nWorkflow Results:")
    print(json.dumps(result, indent=2))

    # Query knowledge graph for workflow results
    workflow_results = coordinator._kg.query(node_type="workflow_step")
    print("\nKnowledge Graph Results:")
    print(json.dumps(workflow_results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())