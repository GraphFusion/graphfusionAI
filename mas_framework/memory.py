from typing import Dict, Any, Optional
from mas_framework.knowledge_graph import KnowledgeGraph, Node, Edge
import json

class Memory:
    """Memory management using Knowledge Graph"""
    
    def __init__(self):
        self.kg = KnowledgeGraph()
        self.context: Dict[str, Any] = {}

    def store(self, key: str, value: Any, context: Optional[Dict[str, Any]] = None):
        """Store information in memory"""
        # Create memory node
        memory_node = Node(
            id=key,
            type="memory",
            properties={"value": value}
        )
        self.kg.add_node(memory_node)

        # Store context if provided
        if context:
            context_node = Node(
                id=f"context_{key}",
                type="context",
                properties=context
            )
            self.kg.add_node(context_node)
            
            # Link memory to context
            edge = Edge(
                source=key,
                target=f"context_{key}",
                type="has_context"
            )
            self.kg.add_edge(edge)

    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve information from memory"""
        node_data = self.kg.get_node(key)
        if not node_data:
            return None

        result = {
            "value": node_data["properties"].get("value"),
            "context": None
        }

        # Get associated context if exists
        neighbors = self.kg.get_neighbors(key)
        for neighbor in neighbors:
            if neighbor["data"]["type"] == "context":
                result["context"] = neighbor["data"]["properties"]

        return result

    def update_context(self, context_update: Dict[str, Any]):
        """Update current context"""
        self.context.update(context_update)

    def clear(self):
        """Clear memory"""
        self.kg = KnowledgeGraph()
        self.context = {}

    def save(self, filepath: str):
        """Save memory state to file"""
        self.kg.save(filepath)
        
        # Save context separately
        with open(f"{filepath}_context.json", 'w') as f:
            json.dump(self.context, f)

    def load(self, filepath: str):
        """Load memory state from file"""
        self.kg.load(filepath)
        
        # Load context
        try:
            with open(f"{filepath}_context.json", 'r') as f:
                self.context = json.load(f)
        except FileNotFoundError:
            self.context = {}
