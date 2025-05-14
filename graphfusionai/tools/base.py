"""
Base classes for tool framework however much of this will change since we have an entire tools framework library, this will be further modified to just serve as connectors or as helper functions to the tool class library...
"""

from typing import Any, Callable, Dict, List, Optional, Union
from pydantic import BaseModel
import inspect
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class ToolMetadata(BaseModel):
    """Metadata for tool registration and discovery"""
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = []
    created_at: datetime = datetime.now()
    requirements: List[str] = []
    permissions: List[str] = []
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

class Tool(BaseModel):
    """Base tool class with metadata and validation"""
    metadata: ToolMetadata
    handler: Callable
    is_async: bool = False
    enabled: bool = True

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create(cls, 
        name: str,
        description: str,
        handler: Callable,
        **metadata_kwargs
    ) -> 'Tool':
        """Create a tool with metadata"""
        # Determine if handler is async
        is_async = inspect.iscoroutinefunction(handler)

        # Create metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            **metadata_kwargs
        )

        # Create tool instance
        return cls(
            metadata=metadata,
            handler=handler,
            is_async=is_async
        )

    def validate_input(self, **kwargs) -> bool:
        """Validate input against schema"""
        if not self.metadata.input_schema:
            return True

        try:
            # Validate required parameters
            for param, param_type in self.metadata.input_schema.items():
                if param not in kwargs:
                    logger.error(f"Missing required parameter: {param}")
                    return False

                try:
                    expected_type = eval(param_type)
                    if not isinstance(kwargs[param], expected_type):
                        logger.error(
                            f"Invalid type for {param}: got {type(kwargs[param]).__name__}, "
                            f"expected {param_type}"
                        )
                        return False
                except (NameError, SyntaxError):
                    logger.error(f"Invalid type specification: {param_type}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            return False

    def validate_output(self, result: Any) -> bool:
        """Validate output against schema"""
        if not self.metadata.output_schema:
            return True

        try:
            # Get expected type
            type_spec = self.metadata.output_schema.get("type")
            if not type_spec:
                logger.error("Output schema missing 'type' specification")
                return False

            try:
                expected_type = eval(type_spec)
                if not isinstance(result, expected_type):
                    logger.error(
                        f"Invalid output type: got {type(result).__name__}, "
                        f"expected {type_spec}"
                    )
                    return False
            except (NameError, SyntaxError):
                logger.error(f"Invalid output type specification: {type_spec}")
                return False

            return True

        except Exception as e:
            logger.error(f"Output validation error: {str(e)}")
            return False

    async def execute(self, **kwargs) -> Any:
        """Execute tool with validation"""
        if not self.enabled:
            raise ValueError(f"Tool {self.metadata.name} is disabled")

        # Validate input
        if not self.validate_input(**kwargs):
            error_msg = f"Invalid input for tool {self.metadata.name}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Execute handler
            if self.is_async:
                result = await self.handler(**kwargs)
            else:
                result = self.handler(**kwargs)

            # Validate output
            if not self.validate_output(result):
                error_msg = f"Invalid output from tool {self.metadata.name}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            return result

        except Exception as e:
            logger.error(f"Error executing tool {self.metadata.name}: {str(e)}")
            raise
