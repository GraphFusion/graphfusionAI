"""
Example demonstrating enhanced memory capabilities
"""

import asyncio
from mas_framework.memory.vectorstore import VectorMemory
from datetime import datetime
import json
import numpy as np

async def main():
    # Initialize memory system
    memory = VectorMemory(dimension=5)  # Using smaller dimension for demo

    # Store some test data
    print("\nStoring test data...")

    # Store with explicit vectors
    space_vector = np.array([0.8, 0.6, 0.9, 0.3, 0.1])  # Space-related
    robot_vector = np.array([0.7, 0.8, 0.2, 0.9, 0.3])  # Robotics-related
    task_vector = np.array([0.1, 0.2, 0.8, 0.7, 0.9])   # Task-related

    # Store with vector
    memory.store(
        "user_1",
        {
            "name": "John Doe",
            "interests": ["AI", "robotics", "space exploration"]
        },
        vector=space_vector,
        metadata={"type": "user_profile"},
        memory_type="long_term"
    )

    # Store with text
    memory.store(
        "project_1",
        {
            "name": "Mars Rover",
            "description": "Autonomous robot for Mars exploration",
            "status": "in_progress"
        },
        text="Mars exploration autonomous robotics project",
        metadata={"type": "project"},
        memory_type="long_term"
    )

    # Store with vector
    memory.store(
        "task_1",
        {
            "title": "Debug navigation system",
            "project": "Mars Rover",
            "priority": "high"
        },
        vector=task_vector,
        metadata={"type": "task"},
        memory_type="short_term",
        ttl=3600  # 1 hour
    )

    # Test retrieval
    print("\nRetrieving data...")
    user = memory.retrieve("user_1")
    print("Retrieved user:", json.dumps(user, indent=2))

    # Test vector similarity search
    print("\nPerforming vector similarity search...")
    space_query = np.array([0.9, 0.5, 0.8, 0.2, 0.1])  # Similar to space_vector
    space_results = memory.search(
        query=space_query,
        limit=2,
        threshold=0.5
    )

    print("\nSpace-related results (vector search):")
    for result in space_results:
        print(f"- {result.key} (score: {result.score:.2f})")
        print(f"  {json.dumps(result.value, indent=2)}")

    # Test text-based search
    print("\nPerforming text-based search...")
    text_results = memory.search(
        query="autonomous robots exploration",
        limit=2,
        threshold=0.3
    )

    print("\nRobotics-related results (text search):")
    for result in text_results:
        print(f"- {result.key} (score: {result.score:.2f})")
        print(f"  {json.dumps(result.value, indent=2)}")

    # Test memory compression
    print("\nCompressing memory...")
    memory.compress()

    # Get memory summary
    print("\nMemory summary:")
    print(memory.summarize())

if __name__ == "__main__":
    asyncio.run(main())