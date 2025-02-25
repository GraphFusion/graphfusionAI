"""
Example demonstrating the new decorator-based agent creation and tool registration.
"""

import asyncio
from mas_framework import Agent, Role
from datetime import datetime

class DataProcessorAgent(Agent):
    """Agent for processing and analyzing data"""
    """Agent for processing and analyzing data"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_tools()

    def _setup_tools(self):
        @self.tool(description="Process raw data into structured format")
        async def process_data(data: dict) -> dict:
            """Process incoming data"""
            return {
                "processed": True,
                "timestamp": datetime.now().isoformat(),
                "result": f"Processed: {data['input']}"
            }

        @self.tool(description="Analyze processed data for insights")
        def analyze_data(data: dict) -> dict:
            """Analyze processed data"""
            return {
                "analyzed": True,
                "insights": ["Insight 1", "Insight 2"],
                "confidence": 0.95
            }

    async def _process_task(self, task: dict) -> dict:
        if task["type"] == "process_data":  # Updated to match capability
            result = await self.execute_tool("process_data", data=task["data"])
            if result["processed"]:
                analysis = await self.execute_tool("analyze_data", data=result)
                return {
                    "processed_data": result,
                    "analysis": analysis
                }
        return {"error": "Unsupported task type"}

async def main():
    # Create agent instance with role
    role = Role(
        name="data_processor",
        capabilities=["process_data", "analyze_data"],
        description="Agent for processing and analyzing data"
    )
    agent = DataProcessorAgent(name="DataProcessor", role=role)

    # Create and execute task
    task = {
        "id": "task1",
        "type": "process_data",  # Updated to match capability
        "data": {
            "input": "Sample data"
        }
    }

    result = await agent.handle_task(task)
    print("\nTask Result:")
    print(result)

    # Display agent capabilities
    print("\nAgent Capabilities:")
    print(f"Role: {agent.role.name}")
    print(f"Capabilities: {agent.role.capabilities}")
    print("\nRegistered Tools:")
    for tool_name, tool in agent._tools.items():
        print(f"- {tool_name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())