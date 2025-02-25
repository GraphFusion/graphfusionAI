"""
Example demonstrating the Tool and Skills Framework functionality
"""

import asyncio
import logging
from mas_framework.tools import (
    Tool, ToolMetadata, ToolRegistry, ToolLoader, ToolValidator
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example tool implementation
class MathTool(Tool):
    """Example tool for basic math operations"""

    def __init__(self):
        super().__init__(
            metadata=ToolMetadata(
                name="math_tool",
                description="Performs basic math operations",
                version="1.0.0",
                tags=["math", "utility"],
                input_schema={
                    "x": "float",
                    "y": "float",
                    "operation": "str"
                },
                output_schema={"type": "float"}
            ),
            handler=self.calculate
        )

    def calculate(self, x: float, y: float, operation: str) -> float:
        """Perform math calculation"""
        if operation == "add":
            return x + y
        elif operation == "subtract":
            return x - y
        elif operation == "multiply":
            return x * y
        elif operation == "divide":
            if y == 0:
                raise ValueError("Division by zero")
            return x / y
        else:
            raise ValueError(f"Unknown operation: {operation}")

async def main():
    # Create registry and loader
    registry = ToolRegistry()
    loader = ToolLoader(registry)
    validator = ToolValidator()

    # Create and validate tool
    math_tool = MathTool()
    validation_result = validator.validate_tool(math_tool)

    if validation_result.valid:
        logger.info("Tool validation successful")
        if validation_result.warnings:
            for warning in validation_result.warnings:
                logger.warning(f"Warning: {warning}")
    else:
        logger.error("Tool validation failed:")
        for error in validation_result.errors:
            logger.error(f"Error: {error}")
        return

    # Register tool
    registry.register(math_tool)

    # List available tools
    tools = registry.list_tools(tags=["math"])
    logger.info(f"Found {len(tools)} math tools:")
    for tool in tools:
        logger.info(f"- {tool.metadata.name}: {tool.metadata.description}")

    # Execute tool
    try:
        tool = registry.get_tool("math_tool")
        if tool:
            # Test successful execution
            result = await tool.execute(x=10, y=5, operation="add")
            logger.info(f"10 + 5 = {result}")

            result = await tool.execute(x=10, y=5, operation="multiply")
            logger.info(f"10 * 5 = {result}")

            # Test input validation
            try:
                await tool.execute(x="invalid", y=5, operation="add")
            except ValueError as e:
                logger.error(f"Input validation caught error: {str(e)}")

            # Test division by zero
            try:
                await tool.execute(x=10, y=0, operation="divide")
            except ValueError as e:
                logger.error(f"Runtime error caught: {str(e)}")

    except Exception as e:
        logger.error(f"Error executing tool: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())