"""Decorators for easy agent capability registration"""

import functools
from typing import Any, Callable, List, Type, TypeVar, cast
from ..base import Agent

T = TypeVar('T', bound=Type[Agent])

def capability(name: str, description: str = None):
    """Decorator to register a method as an agent capability"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._is_capability = True
        wrapper._capability_name = name
        wrapper._capability_description = description
        return wrapper
    return decorator

def agent_template(template_name: str, description: str = None):
    """Class decorator to create an agent from a template"""
    def decorator(cls: T) -> T:
        original_init = cls.__init__
        
        def __init__(self, *args, **kwargs):
            from .factory import AgentFactory
            factory = AgentFactory()
            template = factory.templates.get(template_name)
            if template:
                kwargs['role'] = template.create_role()
            original_init(self, *args, **kwargs)
            
            # Register all methods marked as capabilities
            for name, method in cls.__dict__.items():
                if getattr(method, '_is_capability', False):
                    self.register_capability(
                        method._capability_name,
                        method,
                        method._capability_description
                    )
                    
        cls.__init__ = __init__
        return cast(T, cls)
    return decorator

def auto_capabilities(cls: T) -> T:
    """Class decorator to automatically register public methods as capabilities"""
    original_init = cls.__init__
    
    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        
        # Register all public methods as capabilities
        for name, method in cls.__dict__.items():
            if not name.startswith('_') and callable(method):
                self.register_capability(name, method)
                
    cls.__init__ = __init__
    return cast(T, cls)
