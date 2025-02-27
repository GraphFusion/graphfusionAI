import networkx as nx
from typing import Dict, Any, List, Optional, Tuple, Set
from pydantic import BaseModel
import json
import spacy
from functools import lru_cache
import logging

class Node(BaseModel):
    """Knowledge Graph Node"""
    id: str
    type: str
    properties: Dict[str, Any] = {}

    def validate_type(self) -> bool:
        """Validate node type against allowed types"""
        return self.type in KnowledgeGraph.ALLOWED_NODE_TYPES

class Edge(BaseModel):
    """Knowledge Graph Edge"""
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = {}

    def validate_type(self) -> bool:
        """Validate edge type against allowed types"""
        return self.type in KnowledgeGraph.ALLOWED_EDGE_TYPES

class KnowledgeGraph:
    """Enhanced Knowledge Graph implementation with text extraction and reasoning"""

    # Define allowed types
    ALLOWED_NODE_TYPES = {
        "entity", "concept", "event", "attribute",
        "location", "person", "organization", "date"
    }
    
    ALLOWED_EDGE_TYPES = {
        "has", "is_a", "part_of", "related_to",
        "causes", "located_in", "occurs_at", "belongs_to"
    }

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.logger = logging.getLogger("KnowledgeGraph")
        
        # Initialize NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("Successfully loaded spaCy model")
        except OSError as e:
            self.logger.error(f"Failed to load spaCy model: {str(e)}")
            raise RuntimeError("Failed to initialize NLP model. Please ensure spaCy model is installed.")
        
        # Cache for entity extraction
        self._entity_cache = {}

    def add_node(self, node: Node) -> bool:
        """Add a node to the knowledge graph"""
        try:
            if not node.validate_type():
                self.logger.warning(f"Invalid node type: {node.type}")
                return False
                
            self.graph.add_node(
                node.id,
                type=node.type,
                properties=node.properties
            )
            return True
        except Exception as e:
            self.logger.error(f"Error adding node: {str(e)}")
            return False

    def add_edge(self, edge: Edge) -> bool:
        """Add an edge to the knowledge graph"""
        try:
            if not edge.validate_type():
                self.logger.warning(f"Invalid edge type: {edge.type}")
                return False
                
            if not (self.graph.has_node(edge.source) and self.graph.has_node(edge.target)):
                self.logger.warning("Source or target node does not exist")
                return False
                
            self.graph.add_edge(
                edge.source,
                edge.target,
                type=edge.type,
                properties=edge.properties
            )
            return True
        except Exception as e:
            self.logger.error(f"Error adding edge: {str(e)}")
            return False

    @lru_cache(maxsize=1000)
    def _extract_entities(self, text: str) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Cached entity extraction from text"""
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entity_type = self._map_spacy_type_to_node_type(ent.label_)
            if entity_type:
                entities.append((
                    ent.text,
                    entity_type,
                    {"spacy_label": ent.label_}
                ))
        return entities

    def _map_spacy_type_to_node_type(self, spacy_type: str) -> Optional[str]:
        """Map spaCy entity types to knowledge graph node types"""
        mapping = {
            "PERSON": "person",
            "ORG": "organization",
            "GPE": "location",
            "DATE": "date",
            "EVENT": "event",
            "NORP": "concept",
            "FAC": "location",
            "PRODUCT": "entity"
        }
        return mapping.get(spacy_type)

    def extract_knowledge_from_text(self, text: str) -> List[Tuple[Node, Optional[Edge]]]:
        """Extract knowledge from text and create nodes/edges"""
        try:
            extracted_elements = []
            entities = self._extract_entities(text)
            
            for ent_text, ent_type, props in entities:
                # Create node for entity
                node = Node(
                    id=f"{ent_type}_{len(self.graph.nodes)}",
                    type=ent_type,
                    properties={"text": ent_text, **props}
                )
                
                if self.add_node(node):
                    extracted_elements.append((node, None))
                    
                    # Try to find relationships with existing nodes
                    for other_node in self.graph.nodes:
                        if other_node != node.id:
                            # Simple relationship detection based on proximity
                            edge = Edge(
                                source=node.id,
                                target=other_node,
                                type="related_to"
                            )
                            if self.add_edge(edge):
                                extracted_elements.append((node, edge))
                                
            return extracted_elements
            
        except Exception as e:
            self.logger.error(f"Error extracting knowledge: {str(e)}")
            return []

    def reason(self, query: str) -> List[Dict[str, Any]]:
        """Perform reasoning on the knowledge graph"""
        reasoning_results = []
        query_doc = self.nlp(query)

        # Extract query entities and relationships
        query_entities = list(query_doc.ents)

        for entity in query_entities:
            # Find nodes matching entity type or text
            matching_nodes = []
            for node in self.graph.nodes():
                node_data = self.graph.nodes[node]
                node_props = node_data.get("properties", {})

                # Match by text or type
                if (node_props.get("text", "").lower() == entity.text.lower() or
                    node_data.get("type") == entity.label_):
                    matching_nodes.append(node)

            # Find paths between matching nodes
            for node1 in matching_nodes:
                paths = {}
                for node2 in self.graph.nodes():
                    if node1 != node2:
                        try:
                            all_paths = list(nx.all_simple_paths(self.graph, node1, node2))
                            if all_paths:
                                paths[node2] = all_paths
                        except nx.NetworkXNoPath:
                            continue

                if paths:
                    reasoning_results.append({
                        "query_entity": entity.text,
                        "matched_node": node1,
                        "related_paths": paths
                    })

        return reasoning_results

    def infer_relationships(self) -> List[Edge]:
        """Infer new relationships based on existing patterns"""
        inferred_edges = []

        # Pattern-based inference
        for node1 in self.graph.nodes():
            for node2 in self.graph.nodes():
                if node1 != node2:
                    # Check for transitive relationships
                    paths = list(nx.all_simple_paths(self.graph, node1, node2, cutoff=2))
                    if paths:
                        for path in paths:
                            if len(path) == 3:  # A->B->C pattern
                                edge_type = self._infer_edge_type(path)
                                if edge_type:
                                    inferred_edge = Edge(
                                        source=node1,
                                        target=node2,
                                        type=edge_type,
                                        properties={"inferred": True}
                                    )
                                    inferred_edges.append(inferred_edge)

        return inferred_edges

    def _infer_edge_type(self, path: List[str]) -> Optional[str]:
        """Infer edge type based on path pattern"""
        if len(path) < 3:
            return None

        edge1 = self.graph.get_edge_data(path[0], path[1])
        edge2 = self.graph.get_edge_data(path[1], path[2])

        if not (edge1 and edge2):
            return None

        # Get first edge data since we use MultiDiGraph
        edge1_data = list(edge1.values())[0]
        edge2_data = list(edge2.values())[0]

        edge1_type = edge1_data.get("type")
        edge2_type = edge2_data.get("type")

        # Enhanced inference rules
        if edge1_type == "instance_of" and edge2_type == "subclass_of":
            return "instance_of"
        elif edge1_type == "part_of" and edge2_type == "part_of":
            return "part_of"
        elif edge1_type == "located_in" and edge2_type == "located_in":
            return "located_in"
        elif edge1_type in ["nsubj", "dobj"] and edge2_type in ["nsubj", "dobj"]:
            return "related_to"

        # Infer relationships based on entity types
        node1_type = self.graph.nodes[path[0]].get("type")
        node2_type = self.graph.nodes[path[1]].get("type")
        node3_type = self.graph.nodes[path[2]].get("type")

        if node1_type == "ORG" and node3_type == "ORG":
            return "collaborates_with"
        elif node1_type == "PERSON" and node3_type == "ORG":
            return "affiliated_with"

        return None

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve node data"""
        if node_id in self.graph.nodes:
            return dict(self.graph.nodes[node_id])
        return None

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        """Get neighboring nodes"""
        neighbors = []
        for neighbor in self.graph.neighbors(node_id):
            neighbors.append({
                'id': neighbor,
                'data': dict(self.graph.nodes[neighbor])
            })
        return neighbors

    def query(self, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query nodes by type"""
        results = []
        for node_id in self.graph.nodes:
            node_data = dict(self.graph.nodes[node_id])
            if node_type is None or node_data.get('type') == node_type:
                results.append({
                    'id': node_id,
                    'data': node_data
                })
        return results

    def save(self, filepath: str):
        """Save knowledge graph to file"""
        data = nx.node_link_data(self.graph, edges="edges")  # Explicitly set edges parameter
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def load(self, filepath: str):
        """Load knowledge graph from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.graph = nx.node_link_graph(data, edges="edges")  # Explicitly set edges parameter

    def cleanup(self):
        """Cleanup resources"""
        self._entity_cache.clear()
        self.graph.clear()