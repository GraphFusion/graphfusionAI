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
    timeout: Optional[float] = None  # Timeout in seconds

class TaskOrchestrator:
    """Manages task distribution and execution"""

    def __init__(self):
        self.task_queue = deque()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("TaskOrchestrator")
        self._task_timeouts: Dict[str, asyncio.Task] = {}

    def add_task(self, task: Dict[str, Any]):
        """Add task to queue"""
        # Convert dict to Task if needed
        if isinstance(task, dict):
            task = Task(**task)
        
        # Sort tasks by priority (higher priority first)
        if len(self.task_queue) > 0:
            # Find position to insert based on priority
            for i, existing_task in enumerate(self.task_queue):
                if task.priority > existing_task.priority:
                    self.task_queue.insert(i, task)
                    break
            else:
                self.task_queue.append(task)
        else:
            self.task_queue.append(task)
            
        self.logger.info(f"Task {task.id} added to queue with priority {task.priority}")

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

            # Set up timeout if specified
            if task.timeout:
                try:
                    result = await asyncio.wait_for(
                        agent.handle_task(task.dict()),
                        timeout=task.timeout
                    )
                except asyncio.TimeoutError:
                    self.logger.error(f"Task {task.id} timed out after {task.timeout} seconds")
                    return {
                        "status": "error",
                        "error": f"Task timed out after {task.timeout} seconds",
                        "task_id": task.id
                    }
            else:
                result = await agent.handle_task(task.dict())

            # Store result
            self.completed_tasks[task.id] = result
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]

            return result

        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_id": task.id
            }

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self._task_timeouts:
            self._task_timeouts[task_id].cancel()
            try:
                await self._task_timeouts[task_id]
            except asyncio.CancelledError:
                pass
            del self._task_timeouts[task_id]
            
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
                
            self.logger.info(f"Task {task_id} cancelled")
            return True
            
        return False

    async def cleanup(self):
        """Cleanup all running tasks"""
        for task_id in list(self._task_timeouts.keys()):
            await self.cancel_task(task_id)
        
        self.task_queue.clear()
        self.active_tasks.clear()
        self.logger.info("Task orchestrator cleaned up")

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