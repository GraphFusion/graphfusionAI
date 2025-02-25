"""
Tool registry implementation for plugin system
"""

from typing import Dict, List, Optional, Type
from .base import Tool, ToolMetadata
import logging
import importlib
import pkgutil
from pathlib import Path

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Central registry for tool management and discovery"""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._disabled_tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool in the registry"""
        if not tool.enabled:
            self._disabled_tools[tool.metadata.name] = tool
            logger.info(f"Tool {tool.metadata.name} registered but disabled")
            return
            
        if tool.metadata.name in self._tools:
            raise ValueError(f"Tool {tool.metadata.name} already registered")
            
        self._tools[tool.metadata.name] = tool
        logger.info(f"Tool {tool.metadata.name} registered successfully")
    
    def unregister(self, tool_name: str) -> None:
        """Remove a tool from the registry"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Tool {tool_name} unregistered")
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self._tools.get(tool_name)
    
    def list_tools(self, tags: Optional[List[str]] = None) -> List[Tool]:
        """List registered tools, optionally filtered by tags"""
        if not tags:
            return list(self._tools.values())
            
        return [
            tool for tool in self._tools.values()
            if any(tag in tool.metadata.tags for tag in tags)
        ]
    
    def discover_tools(self, package_path: str) -> List[Tool]:
        """Discover and load tools from a package"""
        discovered = []
        try:
            # Import the package
            package = importlib.import_module(package_path)
            package_dir = Path(package.__file__).parent
            
            # Walk through package
            for _, name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
                if is_pkg:  # Skip if it's a package
                    continue
                    
                try:
                    # Import module
                    module = importlib.import_module(f"{package_path}.{name}")
                    
                    # Look for Tool classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Tool) and 
                            attr != Tool):
                            # Create instance and register
                            tool = attr()
                            self.register(tool)
                            discovered.append(tool)
                            
                except Exception as e:
                    logger.error(f"Error loading tool module {name}: {str(e)}")
                    
            logger.info(f"Discovered {len(discovered)} tools in {package_path}")
            return discovered
            
        except Exception as e:
            logger.error(f"Error discovering tools in {package_path}: {str(e)}")
            return []
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable a disabled tool"""
        if tool_name in self._disabled_tools:
            tool = self._disabled_tools.pop(tool_name)
            tool.enabled = True
            self._tools[tool_name] = tool
            logger.info(f"Tool {tool_name} enabled")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable an enabled tool"""
        if tool_name in self._tools:
            tool = self._tools.pop(tool_name)
            tool.enabled = False
            self._disabled_tools[tool_name] = tool
            logger.info(f"Tool {tool_name} disabled")
            return True
        return False
