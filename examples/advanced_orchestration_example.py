"""
Example demonstrating advanced orchestration capabilities
"""

import asyncio
from mas_framework import Agent, Role
from mas_framework.orchestration import (
    AgentOrchestrator, AgentTemplate, 
    WorkflowCondition, ConditionalTask
)
from mas_framework.task_orchestrator import Task
from datetime import datetime

# Define specialized agents
class DataValidatorAgent(Agent):
    """Agent for validating data"""

    async def _process_task(self, task):
        if task["type"] == "validate":
            data = task["data"]
            # Simulate validation
            is_valid = all(
                isinstance(v, (int, float)) 
                for v in data.get("values", [])
            )
            return {
                "status": "success",
                "data": {
                    "is_valid": is_valid,
                    "timestamp": datetime.now().isoformat()
                }
            }
        return {"status": "error", "error": "Unsupported task type"}

class DataTransformerAgent(Agent):
    """Agent for transforming data"""

    async def _process_task(self, task):
        if task["type"] == "transform":
            data = task["data"]
            # Simulate transformation
            transformed = [v * 2 for v in data.get("values", [])]
            return {
                "status": "success",
                "data": {
                    "transformed": transformed,
                    "timestamp": datetime.now().isoformat()
                }
            }
        return {"status": "error", "error": "Unsupported task type"}

async def main():
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()

    # Register agent templates
    validator_template = AgentTemplate(
        role=Role(
            name="validator",
            capabilities=["validate"],
            description="Validates data format and content"
        ),
        agent_class=DataValidatorAgent
    )

    transformer_template = AgentTemplate(
        role=Role(
            name="transformer",
            capabilities=["transform"],
            description="Transforms and processes data"
        ),
        agent_class=DataTransformerAgent
    )

    orchestrator.register_template("validator", validator_template)
    orchestrator.register_template("transformer", transformer_template)

    # Create tasks for parallel execution
    parallel_tasks = [
        {
            "id": "task1",
            "type": "validate",
            "agent_type": "validator",
            "data": {"values": [1, 2, 3, 4, 5]}
        },
        {
            "id": "task2",
            "type": "validate",
            "agent_type": "validator",
            "data": {"values": [6, 7, "invalid", 9, 10]}
        }
    ]

    print("\nExecuting parallel tasks...")
    parallel_results = await orchestrator.execute_parallel(parallel_tasks)
    print("Parallel execution results:", parallel_results)

    # Create conditional workflow
    conditional_workflow = [
        ConditionalTask(
            task=Task(
                id="validate1",
                type="validate",
                data={"values": [1, 2, 3, 4, 5]},
                assigned_to="validator"  # Explicitly set agent type
            ),
            next_tasks=[
                {
                    "id": "transform1",
                    "type": "transform",
                    "agent_type": "transformer",  # Explicitly set agent type
                    "data": {"values": [1, 2, 3, 4, 5]}
                }
            ]
        ),
        ConditionalTask(
            task=Task(
                id="validate2",
                type="validate",
                data={"values": [6, 7, "invalid", 9, 10]},
                assigned_to="validator"  # Explicitly set agent type
            ),
            condition=WorkflowCondition(
                field="data.is_valid",
                operator="eq",
                value=True
            ),
            next_tasks=[
                {
                    "id": "transform2",
                    "type": "transform",
                    "agent_type": "transformer",  # Explicitly set agent type
                    "data": {"values": [6, 7, 8, 9, 10]}
                }
            ]
        )
    ]

    print("\nExecuting conditional workflow...")
    workflow_results = await orchestrator.execute_conditional(conditional_workflow)
    print("Conditional workflow results:", workflow_results)

if __name__ == "__main__":
    asyncio.run(main())