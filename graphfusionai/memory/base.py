"""
Base memory interfaces and abstractions
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel
import json

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
    """Result of memory query"""
    key: str
    value: Any
    similarity: float
    metadata: Dict[str, Any] = {}

class BaseMemory:
    """Base class for memory implementations"""
    
    def __init__(self):
        """Initialize base memory"""
        self.entries: Dict[str, MemoryEntry] = {}

    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None, vector: Optional[List[float]] = None, memory_type: str = "short_term", ttl: Optional[int] = None) -> bool:
        """Store value in memory with metadata"""
        try:
            self.entries[key] = MemoryEntry(
                key=key,
                value=value,
                metadata=metadata or {},
                vector=vector,
                memory_type=memory_type,
                ttl=ttl
            )
            return True
        except Exception as e:
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value by key"""
        entry = self.entries.get(key)
        return entry.value if entry else None

    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        """Get full memory entry by key"""
        return self.entries.get(key)

    def update(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None, vector: Optional[List[float]] = None, memory_type: str = "short_term", ttl: Optional[int] = None) -> bool:
        """Update existing memory entry"""
        if key not in self.entries:
            return False
            
        try:
            entry = self.entries[key]
            entry.value = value
            if metadata:
                entry.metadata.update(metadata)
            if vector:
                entry.vector = vector
            entry.memory_type = memory_type
            entry.ttl = ttl
            entry.timestamp = datetime.now()
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete memory entry"""
        if key in self.entries:
            del self.entries[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entries"""
        self.entries.clear()

    def list_keys(self) -> List[str]:
        """List all memory keys"""
        return list(self.entries.keys())

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for entry"""
        entry = self.entries.get(key)
        return entry.metadata if entry else None

    def save_to_file(self, filepath: str) -> bool:
        """Save memory to file"""
        try:
            data = {
                key: {
                    "value": entry.value,
                    "timestamp": entry.timestamp.isoformat(),
                    "metadata": entry.metadata,
                    "vector": entry.vector,
                    "memory_type": entry.memory_type,
                    "ttl": entry.ttl
                }
                for key, entry in self.entries.items()
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load_from_file(self, filepath: str) -> bool:
        """Load memory from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.entries = {
                key: MemoryEntry(
                    key=key,
                    value=entry["value"],
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    metadata=entry["metadata"],
                    vector=entry["vector"],
                    memory_type=entry["memory_type"],
                    ttl=entry["ttl"]
                )
                for key, entry in data.items()
            }
            return True
        except Exception:
            return False

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