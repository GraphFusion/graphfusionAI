from graphfusionai import Agent, Role, Memory
from typing import Dict, Any, List, Optional
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime
import numpy as np

class EnhancedDataProcessingAgent(Agent):
    def __init__(self, name: str, role: Role, working_dir: Path):
        super().__init__(name=name, role=role)
        self.working_dir = working_dir
        self.supported_formats = {'.csv', '.json', '.xlsx', '.parquet'}
        self.progress = 0
        
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        # Reset progress for new task
        self.progress = 0
        
        # Validate and process task
        if not self._validate_task(task):
            raise ValueError("Invalid task format")
            
        try:
            if task["type"] == "process_data":
                result = await self._handle_data_processing(task["data"])
            elif task["type"] == "analyze_data":
                result = await self._handle_data_analysis(task["data"])
            else:
                raise ValueError(f"Unsupported task type: {task['type']}")
                
            # Update progress to complete
            self.progress = 100
            return result
            
        except Exception as e:
            # Store error in memory for debugging
            self.memory.store(
                key=f"error_{datetime.now().isoformat()}",
                value={
                    "task": task,
                    "error": str(e),
                    "progress": self.progress
                }
            )
            raise

    def _validate_task(self, task: Dict[str, Any]) -> bool:
        if not isinstance(task, dict):
            return False
            
        required_fields = {"type", "data"}
        if not all(field in task for field in required_fields):
            return False
            
        if task["type"] == "process_data":
            required_data_fields = {"input_file", "output_file"}
            return all(field in task["data"] for field in required_data_fields)
            
        if task["type"] == "analyze_data":
            return "file" in task["data"]
            
        return False

    def _read_file(self, file_path: Path) -> pd.DataFrame:
        self.progress += 10
        
        if file_path.suffix == '.parquet':
            return pq.read_table(file_path).to_pandas()
        elif file_path.suffix == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            return pd.read_json(file_path)
        elif file_path.suffix == '.xlsx':
            return pd.read_excel(file_path)
            
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _validate_dataframe(self, df: pd.DataFrame) -> List[str]:
        """Perform data validation checks."""
        issues = []
        
        # Check for empty dataframe
        if df.empty:
            issues.append("DataFrame is empty")
            
        # Check for missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            issues.append(f"Missing values in columns: {missing_cols}")
            
        # Check for duplicate rows
        if df.duplicated().any():
            issues.append(f"Found {df.duplicated().sum()} duplicate rows")
            
        # Check for incorrect data types
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].dtype == 'object':
                issues.append(f"Column {col} may contain non-numeric values")
                
        return issues

    def _process_dataframe(self, df: pd.DataFrame, operations: list) -> pd.DataFrame:
        progress_per_operation = 70 / len(operations)
        
        for operation in operations:
            if operation["type"] == "filter":
                df = df[df[operation["column"]].isin(operation["values"])]
            elif operation["type"] == "sort":
                df = df.sort_values(operation["column"], 
                                  ascending=operation.get("ascending", True))
            elif operation["type"] == "group":
                df = df.groupby(operation["column"]).agg(operation["aggregations"]).reset_index()
            elif operation["type"] == "remove_duplicates":
                df = df.drop_duplicates(subset=operation.get("columns"))
            elif operation["type"] == "fill_missing":
                method = operation.get("method", "ffill")
                df = df.fillna(method=method)
            elif operation["type"] == "calculate":
                df[operation["new_column"]] = df.eval(operation["formula"])
                
            self.progress += progress_per_operation
            
        return df

    def _analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        # Basic statistics
        stats = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "summary": df.describe(include='all').to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": df.duplicated().sum(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        # Column-specific analysis
        column_analysis = {}
        for col in df.columns:
            column_analysis[col] = {
                "dtype": str(df[col].dtype),
                "unique_values": df[col].nunique(),
                "most_common": df[col].value_counts().head(5).to_dict() if df[col].dtype != 'float64' else None
            }
            
        stats["column_analysis"] = column_analysis
        return stats

    def _save_file(self, df: pd.DataFrame, file_path: Path) -> None:
        # Validate data before saving
        issues = self._validate_dataframe(df)
        if issues:
            self.memory.store(
                key=f"validation_issues_{file_path.stem}",
                value=issues
            )
        
        if file_path.suffix == '.parquet':
            table = pa.Table.from_pandas(df)
            pq.write_table(table, file_path)
        elif file_path.suffix == '.csv':
            df.to_csv(file_path, index=False)
        elif file_path.suffix == '.json':
            df.to_json(file_path)
        elif file_path.suffix == '.xlsx':
            df.to_excel(file_path, index=False)
            
        self.progress += 10

    def get_progress(self) -> int:
        """Return current progress percentage."""
        return self.progress

# Example usage
async def main():
    # Create role with enhanced capabilities
    data_scientist_role = Role(
        name="data_scientist",
        capabilities=["process_data", "analyze_data"],
        description="Enhanced data processing and analysis"
    )
    
    # Create agent
    agent = EnhancedDataProcessingAgent(
        name="EnhancedProcessor",
        role=data_scientist_role,
        working_dir=Path("data")
    )
    
    # Example task with new operations
    task = {
        "type": "process_data",
        "data": {
            "input_file": "input.csv",
            "output_file": "output.parquet",
            "operations": [
                {"type": "remove_duplicates", "columns": ["id", "name"]},
                {"type": "fill_missing", "method": "ffill"},
                {"type": "calculate", "new_column": "total", "formula": "price * quantity"},
                {"type": "sort", "column": "total", "ascending": False}
            ]
        }
    }
    
    try:
        result = await agent.process_task(task)
        print(f"Task completed: {result}")
        print(f"Final progress: {agent.get_progress()}%")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Progress when error occurred: {agent.get_progress()}%")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
