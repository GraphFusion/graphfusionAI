"""
Vectorized memory implementation with semantic search
"""

from typing import Any, Dict, List, Optional, Union, cast
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import json
import logging
from pathlib import Path

from .base import BaseMemory, MemoryEntry, MemoryQueryResult

logger = logging.getLogger(__name__)

class VectorMemory(BaseMemory):
    """Memory implementation with vector storage and semantic search"""

    def __init__(self, dimension: int = 384, cache_dir: Optional[str] = None):
        """Initialize vector memory

        Args:
            dimension: Embedding dimension
            cache_dir: Directory to cache embeddings
        """
        try:
            self.dimension = dimension

            # Memory storage
            self.entries: Dict[str, MemoryEntry] = {}
            self.vectors: List[np.ndarray] = []
            self.keys: List[str] = []

            # Setup caching if enabled
            self.cache_dir = Path(cache_dir) if cache_dir else None
            if self.cache_dir:
                self.cache_dir.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            logger.error(f"Failed to initialize VectorMemory: {str(e)}")
            raise

    def _get_cache_path(self, key: str) -> Optional[Path]:
        """Get cache file path for key"""
        if not self.cache_dir:
            return None
        return self.cache_dir / f"{key}.npy"

    def _text_to_simple_vector(self, text: str) -> np.ndarray:
        """Convert text to a simple vector representation
        This is a basic implementation - for production use a proper embedding model
        """
        try:
            # Create a simple vector based on character frequencies
            freq = np.zeros(self.dimension, dtype=np.float32)

            # Handle long texts by chunking
            chunk_size = 1000  # Process text in chunks
            text = text.lower()

            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                for j, char in enumerate(chunk):
                    freq[j % self.dimension] += ord(char)

            # Normalize
            norm = np.linalg.norm(freq)
            if norm > 0:
                freq = freq / norm
            return freq

        except Exception as e:
            logger.error(f"Failed to convert text to vector: {str(e)}")
            raise ValueError("Text vectorization failed")

    def store(self,
        key: str,
        value: Any,
        vector: Optional[np.ndarray] = None,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        memory_type: str = "short_term",
        ttl: Optional[int] = None
    ) -> None:
        """Store value with vector embedding"""
        try:
            if vector is None and text is not None:
                # Generate vector from text if provided
                vector = self._text_to_simple_vector(text)
                logger.info(f"Generated vector from text for key {key}")
            elif vector is None:
                # Use random vector as fallback
                vector = np.random.randn(self.dimension).astype(np.float32)
                vector = vector / np.linalg.norm(vector)
                logger.warning(f"Using random vector for key {key}")

            # Ensure vector is the right dimension
            if len(vector) != self.dimension:
                raise ValueError(
                    f"Vector dimension mismatch. Expected {self.dimension}, got {len(vector)}"
                )

            # Cache embedding if enabled
            cache_path = self._get_cache_path(key)
            if cache_path:
                np.save(cache_path, vector)

            # Create memory entry
            entry = MemoryEntry(
                key=key,
                value=value,
                metadata=metadata or {},
                vector=cast(List[float], vector.tolist()),
                memory_type=memory_type,
                ttl=ttl,
                timestamp=datetime.now()
            )

            # Store entry and update vectors
            self.entries[key] = entry
            self.vectors.append(vector)
            self.keys.append(key)

        except Exception as e:
            logger.error(f"Failed to store key {key}: {str(e)}")
            raise

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value by key"""
        try:
            entry = self.entries.get(key)
            if not entry:
                return None

            # Check TTL
            if entry.ttl:
                age = (datetime.now() - entry.timestamp).total_seconds()
                if age > entry.ttl:
                    self.forget(key)
                    return None

            return entry.value

        except Exception as e:
            logger.error(f"Failed to retrieve key {key}: {str(e)}")
            raise

    def search(self, 
        query: Union[str, np.ndarray],
        limit: int = 5,
        threshold: float = 0.5,
        memory_type: Optional[str] = None
    ) -> List[MemoryQueryResult]:
        """Search memory using vector similarity

        Args:
            query: Query text or vector to compare against
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)
            memory_type: Filter by memory type
        """
        try:
            if not self.vectors:
                return []

            # Convert query to vector if it's text
            query_vector = query if isinstance(query, np.ndarray) else self._text_to_simple_vector(query)

            # Ensure query vector is the right dimension
            if len(query_vector) != self.dimension:
                raise ValueError(
                    f"Query vector dimension mismatch. Expected {self.dimension}, got {len(query_vector)}"
                )

            # Calculate similarities
            vectors = np.array(self.vectors, dtype=np.float32)
            similarities = cosine_similarity([query_vector], vectors)[0]

            # Get top results
            indices = np.argsort(similarities)[::-1][:limit]

            results = []
            for idx in indices:
                score = similarities[idx]
                if score < threshold:
                    continue

                key = self.keys[idx]
                entry = self.entries[key]

                # Skip if memory type doesn't match
                if memory_type and entry.memory_type != memory_type:
                    continue

                results.append(MemoryQueryResult(
                    key=key,
                    value=entry.value,
                    score=float(score),
                    metadata=entry.metadata
                ))

            return results

        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            raise

    def forget(self, key: str) -> None:
        """Remove entry from memory"""
        try:
            if key in self.entries:
                idx = self.keys.index(key)
                self.entries.pop(key)
                self.vectors.pop(idx)
                self.keys.pop(idx)

                # Remove cached embedding
                cache_path = self._get_cache_path(key)
                if cache_path and cache_path.exists():
                    cache_path.unlink()

        except Exception as e:
            logger.error(f"Failed to forget key {key}: {str(e)}")
            raise

    def compress(self, max_age: int = 3600) -> None:
        """Compress memory by removing old short-term memories

        Args:
            max_age: Maximum age in seconds for short-term memories
        """
        try:
            keys_to_remove = []

            for key, entry in self.entries.items():
                if entry.memory_type == "short_term":
                    age = (datetime.now() - entry.timestamp).total_seconds()
                    if age > max_age:
                        keys_to_remove.append(key)

            for key in keys_to_remove:
                self.forget(key)

            logger.info(f"Compressed {len(keys_to_remove)} memories")

        except Exception as e:
            logger.error(f"Failed to compress memory: {str(e)}")
            raise

    def summarize(self, keys: Optional[List[str]] = None) -> str:
        """Generate summary of memory contents"""
        try:
            entries = []
            if keys:
                entries = [self.entries[k] for k in keys if k in self.entries]
            else:
                entries = list(self.entries.values())

            summary = {
                "total_entries": len(entries),
                "memory_types": {
                    "short_term": len([e for e in entries if e.memory_type == "short_term"]),
                    "long_term": len([e for e in entries if e.memory_type == "long_term"])
                },
                "latest_entries": [
                    {
                        "key": e.key,
                        "timestamp": e.timestamp.isoformat(),
                        "memory_type": e.memory_type,
                        "metadata": e.metadata
                    }
                    for e in sorted(entries, key=lambda x: x.timestamp, reverse=True)[:5]
                ]
            }

            return json.dumps(summary, indent=2)

        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            raise