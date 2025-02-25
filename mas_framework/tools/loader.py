"""
Plugin loader for dynamic tool loading
"""

from typing import List, Optional, Dict
from pathlib import Path
import importlib.util
import logging
from .base import Tool
from .validator import ToolValidator
from .registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolLoader:
    """Handles dynamic loading of tool plugins"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.validator = ToolValidator()
    
    def load_from_path(self, 
        path: str, 
        validate: bool = True
    ) -> List[Tool]:
        """Load tools from a directory path"""
        loaded_tools = []
        try:
            plugin_path = Path(path)
            if not plugin_path.exists():
                logger.error(f"Plugin path does not exist: {path}")
                return []
            
            # Load all .py files
            for file_path in plugin_path.glob("*.py"):
                if file_path.name.startswith("_"):
                    continue
                    
                try:
                    # Import module
                    spec = importlib.util.spec_from_file_location(
                        file_path.stem, str(file_path)
                    )
                    if spec is None or spec.loader is None:
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find and load tools
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Tool) and 
                            attr != Tool):
                            # Create instance
                            tool = attr()
                            
                            # Validate if required
                            if validate:
                                result = self.validator.validate_tool(tool)
                                if not result.valid:
                                    logger.warning(
                                        f"Tool validation failed for {tool.metadata.name}: "
                                        f"{', '.join(result.errors)}"
                                    )
                                    continue
                                    
                                if result.warnings:
                                    for warning in result.warnings:
                                        logger.warning(
                                            f"Tool {tool.metadata.name}: {warning}"
                                        )
                            
                            # Register tool
                            self.registry.register(tool)
                            loaded_tools.append(tool)
                            
                except Exception as e:
                    logger.error(f"Error loading plugin {file_path}: {str(e)}")
                    
            logger.info(f"Loaded {len(loaded_tools)} tools from {path}")
            return loaded_tools
            
        except Exception as e:
            logger.error(f"Error loading plugins from {path}: {str(e)}")
            return []
    
    def load_from_module(self,
        module_name: str,
        validate: bool = True
    ) -> List[Tool]:
        """Load tools from a Python module"""
        try:
            # Import module
            module = importlib.import_module(module_name)
            loaded_tools = []
            
            # Find and load tools
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Tool) and 
                    attr != Tool):
                    try:
                        # Create instance
                        tool = attr()
                        
                        # Validate if required
                        if validate:
                            result = self.validator.validate_tool(tool)
                            if not result.valid:
                                logger.warning(
                                    f"Tool validation failed for {tool.metadata.name}: "
                                    f"{', '.join(result.errors)}"
                                )
                                continue
                                
                            if result.warnings:
                                for warning in result.warnings:
                                    logger.warning(
                                        f"Tool {tool.metadata.name}: {warning}"
                                    )
                        
                        # Register tool
                        self.registry.register(tool)
                        loaded_tools.append(tool)
                        
                    except Exception as e:
                        logger.error(
                            f"Error loading tool {attr_name} from {module_name}: {str(e)}"
                        )
            
            logger.info(f"Loaded {len(loaded_tools)} tools from module {module_name}")
            return loaded_tools
            
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {str(e)}")
            return []
