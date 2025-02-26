"""
Tool validation and safety checks
"""

from typing import List, Optional, Dict, Any
from .base import Tool, ToolMetadata
import logging
import inspect
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    """Results of tool validation"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []

class ToolValidator:
    """Validates tools for safety and correctness"""
    
    @staticmethod
    def validate_tool(tool: Tool) -> ValidationResult:
        """Validate a tool's configuration and implementation"""
        errors = []
        warnings = []
        
        try:
            # Check metadata
            if not tool.metadata.name:
                errors.append("Tool name is required")
            if not tool.metadata.description:
                errors.append("Tool description is required")
                
            # Validate handler
            if not tool.handler:
                errors.append("Tool handler is required")
            elif not callable(tool.handler):
                errors.append("Tool handler must be callable")
            else:
                # Check handler signature
                sig = inspect.signature(tool.handler)
                if tool.metadata.input_schema:
                    for param_name in tool.metadata.input_schema:
                        if param_name not in sig.parameters:
                            errors.append(f"Handler missing parameter: {param_name}")
                
            # Check permissions
            if tool.metadata.permissions:
                for perm in tool.metadata.permissions:
                    if not ToolValidator._validate_permission(perm):
                        warnings.append(f"Unknown permission: {perm}")
                
            # Validate requirements
            if tool.metadata.requirements:
                missing = ToolValidator._check_requirements(
                    tool.metadata.requirements
                )
                for req in missing:
                    warnings.append(f"Missing requirement: {req}")
                    
            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    @staticmethod
    def _validate_permission(permission: str) -> bool:
        """Validate if a permission is recognized"""
        valid_permissions = {
            "filesystem.read",
            "filesystem.write",
            "network.connect",
            "process.execute"
        }
        return permission in valid_permissions
    
    @staticmethod
    def _check_requirements(requirements: List[str]) -> List[str]:
        """Check if requirements are installed"""
        missing = []
        for req in requirements:
            try:
                __import__(req.split(">=")[0].split("==")[0].strip())
            except ImportError:
                missing.append(req)
        return missing
    
    @staticmethod
    def validate_input(tool: Tool, **kwargs) -> ValidationResult:
        """Validate input parameters against schema"""
        if not tool.metadata.input_schema:
            return ValidationResult(valid=True)
            
        errors = []
        try:
            # Validate required parameters
            for param, param_type in tool.metadata.input_schema.items():
                if param not in kwargs:
                    errors.append(f"Missing required parameter: {param}")
                elif not isinstance(kwargs[param], eval(param_type)):
                    errors.append(
                        f"Invalid type for {param}: expected {param_type}"
                    )
            
            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors
            )
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Input validation error: {str(e)}"]
            )
    
    @staticmethod
    def validate_output(tool: Tool, result: Any) -> ValidationResult:
        """Validate output against schema"""
        if not tool.metadata.output_schema:
            return ValidationResult(valid=True)
            
        try:
            # Validate output type
            expected_type = eval(tool.metadata.output_schema["type"])
            if not isinstance(result, expected_type):
                return ValidationResult(
                    valid=False,
                    errors=[f"Invalid output type: expected {expected_type.__name__}"]
                )
            
            return ValidationResult(valid=True)
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Output validation error: {str(e)}"]
            )
