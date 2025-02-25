"""
Memory module initialization
"""

from .base import BaseMemory, MemoryEntry, MemoryQueryResult
from .vectorstore import VectorMemory

# Make VectorMemory the default Memory implementation
Memory = VectorMemory

__all__ = [
    "BaseMemory",
    "Memory",
    "MemoryEntry",
    "MemoryQueryResult",
    "VectorMemory"
]