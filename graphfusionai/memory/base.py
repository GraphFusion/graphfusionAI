"""
Base memory interfaces and abstractions
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel

class MemoryEntry(BaseModel):
    """Memory entry with metadata"""
    key: str
    value: Any
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}
    vector: Optional[List[float]] = None
    memory_type: str = "short_term"  # short_term or long_term
    ttl: Optional[int] = None  # Time to live in seconds

class MemoryQueryResult(BaseModel):
    """Query result with similarity score"""
    key: str
    value: Any
    score: float
    metadata: Dict[str, Any]

class BaseMemory:
    """Base memory interface"""

    def store(self, key: str, value: Any, vector: Optional[List[float]] = None, **kwargs) -> None:
        """Store value in memory with optional vector embedding"""
        raise NotImplementedError

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value by key"""
        raise NotImplementedError

    def search(self, query: Union[str, List[float]], limit: int = 5) -> List[MemoryQueryResult]:
        """Search memory using semantic or vector similarity"""
        raise NotImplementedError

    def forget(self, key: str) -> None:
        """Remove entry from memory"""
        raise NotImplementedError

    def compress(self) -> None:
        """Compress and optimize memory storage"""
        raise NotImplementedError

    def summarize(self, keys: Optional[List[str]] = None) -> str:
        """Generate summary of memory contents"""
        raise NotImplementedError