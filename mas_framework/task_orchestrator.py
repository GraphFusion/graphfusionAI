from typing import Dict, List, Any, Optional
from collections import deque
from pydantic import BaseModel
import asyncio
import logging
from datetime import datetime

class Task(BaseModel):
    """Task definition"""
    id: str
    type: str
    priority: int = 1
    data: Dict[str, Any]
    assigned_to: Optional[str] = None
    status: str = "pending"
    created_at: datetime = datetime.now()

class TaskOrchestrator:
    """Manages task distribution and execution"""

    def __init__(self):
        self.task_queue = deque()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("TaskOrchestrator")

    def add_task(self, task: Dict[str, Any]):
        """Add task to queue"""
        # Convert dict to Task if needed
        if isinstance(task, dict):
            task = Task(**task)
        self.task_queue.append(task)
        self.logger.info(f"Task {task.id} added to queue")

    def get_next_task(self) -> Optional[Task]:
        """Get next task from queue"""
        if self.task_queue:
            task = self.task_queue.popleft()
            self.active_tasks[task.id] = task
            return task
        return None

    async def execute_task(self, agent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with given agent"""
        try:
            # Convert dict to Task if needed
            if isinstance(task, dict):
                task = Task(**task)

            self.logger.info(f"Executing task {task.id} with agent {agent.name}")
            result = await agent.handle_task(task.dict())

            if result.get("status") == "success":
                self.completed_tasks[task.id] = result
                self.logger.info(f"Task {task.id} completed successfully")
            else:
                self.logger.error(f"Task {task.id} failed: {result.get('error')}")
                self.task_queue.append(task)  # Retry failed tasks

            return result
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_id": task.id
            }

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of specific task"""
        if task_id in self.completed_tasks:
            return {
                "status": "completed",
                "result": self.completed_tasks[task_id]
            }
        elif task_id in self.active_tasks:
            return {
                "status": "active",
                "task": self.active_tasks[task_id]
            }
        else:
            return {"status": "not_found"}