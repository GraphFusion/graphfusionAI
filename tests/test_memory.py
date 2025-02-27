"""Tests for Memory functionality"""

import pytest
import numpy as np
from graphfusionai.memory import Memory
from graphfusionai.memory.vectorstore import VectorMemory

@pytest.fixture
def vector_memory():
    return VectorMemory(dimension=5)

def test_memory_initialization(vector_memory):
    """Test memory initialization"""
    assert vector_memory.dimension == 5
    assert len(vector_memory.entries) == 0
    assert len(vector_memory.vectors) == 0
    assert len(vector_memory.keys) == 0

def test_memory_store_and_retrieve(vector_memory):
    """Test storing and retrieving values"""
    test_vector = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
    vector_memory.store(
        key="test_key",
        value={"data": "test"},
        vector=test_vector,
        metadata={"type": "test"}
    )

    result = vector_memory.retrieve("test_key")
    assert result == {"data": "test"}
    assert "test_key" in vector_memory.entries
    assert len(vector_memory.vectors) == 1

def test_memory_text_storage(vector_memory):
    """Test storing with text"""
    vector_memory.store(
        key="text_key",
        value="test value",
        text="This is a test document"
    )

    result = vector_memory.retrieve("text_key")
    assert result == "test value"
    assert len(vector_memory.vectors) == 1

def test_memory_search(vector_memory):
    """Test vector similarity search"""
    # Store some test entries
    vector_memory.store(
        key="space",
        value="space content",
        vector=np.array([0.8, 0.6, 0.9, 0.3, 0.1], dtype=np.float32)
    )
    vector_memory.store(
        key="robots",
        value="robot content",
        vector=np.array([0.7, 0.8, 0.2, 0.9, 0.3], dtype=np.float32)
    )

    # Search with a vector similar to space
    results = vector_memory.search(
        query=np.array([0.9, 0.5, 0.8, 0.2, 0.1], dtype=np.float32),
        limit=1
    )
    assert len(results) == 1
    assert results[0].key == "space"

def test_memory_ttl(vector_memory):
    """Test time-to-live functionality"""
    vector_memory.store(
        key="temp",
        value="temporary",
        text="temporary content",
        ttl=0  # Expire immediately
    )
    
    assert vector_memory.retrieve("temp") is None

def test_memory_compression(vector_memory):
    """Test memory compression"""
    # Store entries with TTL
    vector_memory.store(
        key="temp1",
        value="temp1",
        text="temp1",
        ttl=0
    )
    vector_memory.store(
        key="temp2",
        value="temp2",
        text="temp2",
        ttl=0
    )

    # Compress memory
    vector_memory.compress()
    
    # Check that expired entries are removed
    assert "temp1" not in vector_memory.entries
    assert "temp2" not in vector_memory.entries

def test_memory_forget(vector_memory):
    """Test forgetting entries"""
    vector_memory.store(
        key="forget_me",
        value="test",
        text="test"
    )
    
    vector_memory.forget("forget_me")
    assert "forget_me" not in vector_memory.entries
    assert len(vector_memory.vectors) == 0
    assert len(vector_memory.keys) == 0
