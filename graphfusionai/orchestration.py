"""
Advanced orchestration capabilities for dynamic agent creation and management
"""

from typing import Dict, List, Any, Optional, Type, Union
from pydantic import BaseModel
import asyncio
from uuid import uuid4

from .agent import Agent, Role
from .task_orchestrator import Task

class AgentTemplate(BaseModel):
    """Template for dynamic agent creation"""
    role: Role
    agent_class: Type[Agent]
    init_params: Dict[str, Any] = {}

class WorkflowCondition(BaseModel):
    """Defines conditions for workflow execution"""
    field: str  # The field to check in the task result
    operator: str  # 'eq', 'gt', 'lt', 'contains'
    value: Any

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate the condition against data"""
        try:
            # Navigate nested dictionary using dot notation
            field_value = data
            for key in self.field.split('.'):
                field_value = field_value[key]

            if self.operator == "eq":
                return field_value == self.value
            elif self.operator == "gt":
                return field_value > self.value
            elif self.operator == "lt":
                return field_value < self.value
            elif self.operator == "contains":
                return self.value in field_value
            return False
        except (KeyError, TypeError):
            return False

class ConditionalTask(BaseModel):
    """Task with conditional execution"""
    task: Task
    condition: Optional[WorkflowCondition] = None
    next_tasks: List[Dict[str, Any]] = []  # List of task configurations

class AgentOrchestrator:
    """Advanced orchestration for dynamic agent creation and management"""

    def __init__(self):
        self.agent_templates: Dict[str, AgentTemplate] = {}
        self.active_agents: Dict[str, Agent] = {}
        self.task_results: Dict[str, Any] = {}

    def register_template(self, name: str, template: AgentTemplate):
        """Register an agent template"""
        self.agent_templates[name] = template

    def create_agent(self, template_name: str, agent_name: Optional[str] = None) -> Agent:
        """Create a new agent from template"""
        if template_name not in self.agent_templates:
            raise ValueError(f"Template {template_name} not found")

        template = self.agent_templates[template_name]
        agent_name = agent_name or f"{template_name}_{str(uuid4())[:8]}"

        # Create agent instance
        agent = template.agent_class(
            name=agent_name,
            role=template.role,
            **template.init_params
        )

        self.active_agents[agent.id] = agent
        return agent

    async def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple tasks in parallel"""
        async def execute_single(task: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Get or create agent based on task requirements
                agent = None
                if "agent_id" in task and task["agent_id"] in self.active_agents:
                    agent = self.active_agents[task["agent_id"]]
                elif "agent_type" in task and task["agent_type"] in self.agent_templates:
                    agent = self.create_agent(task["agent_type"])

                if not agent:
                    raise ValueError(f"No valid agent specified for task: {task}")

                result = await agent.handle_task(task)
                self.task_results[task["id"]] = result
                return result
            except Exception as e:
                return {"status": "error", "error": str(e)}

        # Execute all tasks in parallel
        results = await asyncio.gather(
            *[execute_single(task) for task in tasks]
        )

        return results

    async def execute_conditional(self, workflow: List[ConditionalTask]) -> List[Dict[str, Any]]:
        """Execute a conditional workflow"""
        results = []

        for step in workflow:
            try:
                # Check condition if present
                if step.condition:
                    # Get the most recent result for condition evaluation
                    latest_result = self.task_results.get(
                        step.task.id,
                        results[-1] if results else {}
                    )
                    if not step.condition.evaluate(latest_result):
                        continue

                # Execute the task
                task_dict = step.task.dict()

                # Get agent type from assigned_to or task properties
                agent_type = None
                if hasattr(step.task, "assigned_to") and step.task.assigned_to:
                    agent_type = step.task.assigned_to
                elif "agent_type" in task_dict:
                    agent_type = task_dict["agent_type"]

                if not agent_type:
                    raise ValueError("No agent type specified for task")

                # Set agent type for the task
                task_dict["agent_type"] = agent_type
                task_result = await self.execute_parallel([task_dict])
                results.extend(task_result)

                # Process next tasks if any and task was successful
                if step.next_tasks and task_result[0].get("status") == "success":
                    # Add agent type to next tasks if not specified
                    for next_task in step.next_tasks:
                        if "agent_type" not in next_task and "agent_id" not in next_task:
                            next_task["agent_type"] = agent_type

                    next_results = await self.execute_parallel(step.next_tasks)
                    results.extend(next_results)

            except Exception as e:
                results.append({
                    "status": "error",
                    "error": str(e),
                    "task_id": step.task.id if hasattr(step.task, "id") else None
                })

        return results