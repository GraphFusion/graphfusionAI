# Module 2: Building Your First Agent

## Learning Objectives
By the end of this module, you will:
- Understand agent architecture in depth
- Learn to define complex roles with multiple capabilities
- Implement a data processing agent
- Handle asynchronous operations effectively

## 1. Agent Architecture Deep Dive

### Core Components
```python
class Agent:
    def __init__(self, name: str, role: Role):
        self.name = name
        self.role = role
        self.state = {}
        self.memory = Memory()

    async def process_task(self, task: Dict[str, Any]) -> Any:
        # Public interface
        pass

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # To be implemented by subclasses
        raise NotImplementedError
```

Key concepts:
- **Name**: Unique identifier for the agent
- **Role**: Defines capabilities and permissions
- **State**: Current agent status
- **Memory**: Long-term storage
- **Task Processing**: Core logic implementation

## 2. Advanced Role Definition

```python
from graphfusionai import Role, Capability

# Define capabilities with constraints
data_processing = Capability(
    name="process_data",
    required_permissions=["read_files", "write_files"],
    rate_limit=100  # tasks per minute
)

data_analysis = Capability(
    name="analyze_data",
    required_permissions=["read_files"],
    rate_limit=50
)

# Create comprehensive role
data_scientist_role = Role(
    name="data_scientist",
    capabilities=[data_processing, data_analysis],
    description="Processes and analyzes data sets",
    metadata={
        "department": "Analytics",
        "access_level": "senior"
    }
)
```

## 3. Building a Data Processing Agent

Let's create a practical agent that processes data files:

```python
from graphfusionai import Agent, Role, Memory
from typing import Dict, Any
import pandas as pd
from pathlib import Path

class DataProcessingAgent(Agent):
    def __init__(self, name: str, role: Role, working_dir: Path):
        super().__init__(name=name, role=role)
        self.working_dir = working_dir
        self.supported_formats = {'.csv', '.json', '.xlsx'}

    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Validate task
        if not self._validate_task(task):
            raise ValueError("Invalid task format")

        # Process based on task type
        if task["type"] == "process_data":
            return await self._handle_data_processing(task["data"])
        elif task["type"] == "analyze_data":
            return await self._handle_data_analysis(task["data"])
        
        raise ValueError(f"Unsupported task type: {task['type']}")

    def _validate_task(self, task: Dict[str, Any]) -> bool:
        required_fields = {"type", "data"}
        return all(field in task for field in required_fields)

    async def _handle_data_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        input_file = self.working_dir / data["input_file"]
        output_file = self.working_dir / data["output_file"]

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if input_file.suffix not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {input_file.suffix}")

        # Process the file
        df = self._read_file(input_file)
        processed_df = self._process_dataframe(df, data.get("operations", []))
        self._save_file(processed_df, output_file)

        # Update agent state
        self.state.update({
            "last_processed_file": str(input_file),
            "last_processed_time": pd.Timestamp.now().isoformat()
        })

        # Store in memory
        self.memory.store(
            key=f"processed_{input_file.stem}",
            value={
                "input": str(input_file),
                "output": str(output_file),
                "operations": data.get("operations", [])
            }
        )

        return {
            "status": "success",
            "input_file": str(input_file),
            "output_file": str(output_file),
            "operations_applied": len(data.get("operations", []))
        }

    async def _handle_data_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        file_path = self.working_dir / data["file"]
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df = self._read_file(file_path)
        analysis = self._analyze_dataframe(df)

        return {
            "status": "success",
            "file": str(file_path),
            "analysis": analysis
        }

    def _read_file(self, file_path: Path) -> pd.DataFrame:
        if file_path.suffix == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            return pd.read_json(file_path)
        elif file_path.suffix == '.xlsx':
            return pd.read_excel(file_path)
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _process_dataframe(self, df: pd.DataFrame, operations: list) -> pd.DataFrame:
        for operation in operations:
            if operation["type"] == "filter":
                df = df[df[operation["column"]].isin(operation["values"])]
            elif operation["type"] == "sort":
                df = df.sort_values(operation["column"], ascending=operation.get("ascending", True))
            elif operation["type"] == "group":
                df = df.groupby(operation["column"]).agg(operation["aggregations"]).reset_index()
        return df

    def _analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "summary": df.describe().to_dict(),
            "missing_values": df.isnull().sum().to_dict()
        }

    def _save_file(self, df: pd.DataFrame, file_path: Path) -> None:
        if file_path.suffix == '.csv':
            df.to_csv(file_path, index=False)
        elif file_path.suffix == '.json':
            df.to_json(file_path)
        elif file_path.suffix == '.xlsx':
            df.to_excel(file_path, index=False)
```

## Exercise: Enhance the Data Processing Agent

1. Add support for a new file format (e.g., parquet)
2. Implement new data processing operations:
   - Remove duplicates
   - Fill missing values
   - Create new calculated columns
3. Add data validation checks
4. Implement progress tracking for long-running operations

## Solution
Check the [exercise solution](exercise_solution.py) for a complete implementation.

## Next Steps
- Review the [API Reference](../../api_reference.md)
- Explore the [example notebooks](../../examples/)
- Move on to [Module 3](../module3/README.md) to learn about state management and memory systems
