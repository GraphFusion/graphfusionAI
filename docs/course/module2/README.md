# Module 2: Building Your First Agent

## Learning Objectives
By the end of this module, you will:
- Understand agent architecture in depth
- Create custom roles with specific capabilities
- Implement stateful agents
- Handle complex tasks and error conditions

## 1. Agent Architecture Deep Dive

### Core Components
```python
class CustomAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.state = {}  # Internal state
        
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Main task processing logic
        pass
        
    async def _pre_process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Task validation and preparation
        pass
        
    async def _post_process(self, result: Any) -> Any:
        # Result processing and cleanup
        pass
```

## 2. Creating Custom Roles

Roles define what an agent can do:

```python
from graphfusionai import Role

data_processor_role = Role(
    name="data_processor",
    capabilities=[
        "process_csv",
        "process_json",
        "validate_data",
        "transform_data"
    ],
    description="Processes and validates various data formats"
)
```

## 3. Implementing a Data Processing Agent

```python
from graphfusionai import Agent, Role
from typing import Dict, Any
import json
import csv
from io import StringIO

class DataProcessorAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.state = {
            "processed_files": 0,
            "last_operation": None,
            "error_count": 0
        }

    async def _pre_process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if "type" not in task:
            raise ValueError("Task must specify operation type")
        if "data" not in task:
            raise ValueError("Task must include data")
        return task

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        self.state["last_operation"] = task["type"]
        
        try:
            if task["type"] == "process_csv":
                return await self._process_csv(task["data"])
            elif task["type"] == "process_json":
                return await self._process_json(task["data"])
            elif task["type"] == "validate_data":
                return await self._validate_data(task["data"])
            elif task["type"] == "transform_data":
                return await self._transform_data(task["data"])
            else:
                raise ValueError(f"Unsupported task type: {task['type']}")
        except Exception as e:
            self.state["error_count"] += 1
            raise

    async def _post_process(self, result: Any) -> Any:
        self.state["processed_files"] += 1
        return {
            "result": result,
            "stats": {
                "processed_files": self.state["processed_files"],
                "error_count": self.state["error_count"]
            }
        }

    async def _process_csv(self, data: str) -> Dict[str, Any]:
        f = StringIO(data)
        reader = csv.DictReader(f)
        return {"rows": [row for row in reader]}

    async def _process_json(self, data: str) -> Dict[str, Any]:
        return {"data": json.loads(data)}

    async def _validate_data(self, data: Dict[str, Any]) -> Dict[str, bool]:
        required_fields = data.get("required_fields", [])
        target_data = data.get("target_data", {})
        
        missing_fields = [
            field for field in required_fields 
            if field not in target_data
        ]
        
        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields
        }

    async def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        transforms = data.get("transforms", [])
        target_data = data.get("target_data", {})
        
        result = dict(target_data)
        for transform in transforms:
            field = transform["field"]
            operation = transform["operation"]
            
            if operation == "uppercase" and field in result:
                result[field] = result[field].upper()
            elif operation == "lowercase" and field in result:
                result[field] = result[field].lower()
                
        return {"transformed_data": result}
```

## Exercise: Enhanced Data Processor

1. Extend the `DataProcessorAgent` to:
   - Add support for XML processing
   - Implement data type validation
   - Add data transformation for numerical operations
   - Track processing time in the agent's state

2. Create test cases that:
   - Process multiple file formats
   - Handle invalid data gracefully
   - Measure performance metrics

## Next Steps
- Check the [exercise solution](exercise_solution.py)
- Review the [API Reference](../../api_reference.md)
- Continue to [Module 3](../module3/README.md) for advanced agent capabilities
