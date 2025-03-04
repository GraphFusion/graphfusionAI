from graphfusionai import Agent, Role
from typing import Dict, Any

# Enhanced role with farewell capability
enhanced_role = Role(
    name="greeting_agent",
    capabilities=["greet", "farewell"],
    description="An agent that can greet and say goodbye"
)

class EnhancedGreetingAgent(Agent):
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Validate task structure
        if not isinstance(task, dict):
            raise ValueError("Task must be a dictionary")
        
        if "type" not in task:
            raise ValueError("Task must have a 'type' field")
        
        if "data" not in task:
            task["data"] = {}
            
        if not isinstance(task["data"], dict):
            raise ValueError("Task data must be a dictionary")

        # Process task based on type
        if task["type"] == "greet":
            name = task["data"].get("name", "World")
            if not isinstance(name, str):
                raise ValueError("Name must be a string")
            return f"Hello, {name}!"
            
        elif task["type"] == "farewell":
            name = task["data"].get("name", "World")
            if not isinstance(name, str):
                raise ValueError("Name must be a string")
            return f"Goodbye, {name}! Have a great day!"
            
        raise ValueError(f"Unsupported task type: {task['type']}")

async def main():
    # Create agent instance
    agent = EnhancedGreetingAgent(name="EnhancedGreeter", role=enhanced_role)
    
    # Test valid cases
    tasks = [
        {"type": "greet", "data": {"name": "Alice"}},
        {"type": "farewell", "data": {"name": "Bob"}},
        {"type": "greet", "data": {}},  # Uses default name
    ]
    
    print("Testing valid cases:")
    for task in tasks:
        result = await agent.process_task(task)
        print(f"Task: {task}\nResult: {result}\n")
    
    # Test error cases
    error_tasks = [
        {"type": "unknown", "data": {}},  # Invalid task type
        {"type": "greet", "data": {"name": 123}},  # Invalid name type
        "invalid_task",  # Invalid task structure
    ]
    
    print("Testing error cases:")
    for task in error_tasks:
        try:
            result = await agent.process_task(task)
        except Exception as e:
            print(f"Task: {task}\nError: {str(e)}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
