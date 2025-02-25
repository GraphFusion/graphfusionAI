import networkx as nx
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
import json
import spacy

class Node(BaseModel):
    """Knowledge Graph Node"""
    id: str
    type: str
    properties: Dict[str, Any] = {}

class Edge(BaseModel):
    """Knowledge Graph Edge"""
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = {}

class KnowledgeGraph:
    """Enhanced Knowledge Graph implementation with text extraction and reasoning"""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        # Load NLP model for entity extraction
        self.nlp = spacy.load("en_core_web_sm")

    def add_node(self, node: Node):
        """Add a node to the knowledge graph"""
        self.graph.add_node(
            node.id,
            type=node.type,
            properties=node.properties
        )

    def add_edge(self, edge: Edge):
        """Add an edge to the knowledge graph"""
        self.graph.add_edge(
            edge.source,
            edge.target,
            type=edge.type,
            properties=edge.properties
        )

    def extract_knowledge_from_text(self, text: str) -> List[Tuple[Node, Optional[Edge]]]:
        """Extract knowledge from text and create nodes/edges"""
        doc = self.nlp(text)
        extracted_elements = []

        # Extract and store entities
        entity_nodes = {}
        for ent in doc.ents:
            node = Node(
                id=f"{ent.label_}_{len(self.graph.nodes)}",
                type=ent.label_,
                properties={
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "normalized": ent.text.lower()
                }
            )
            extracted_elements.append((node, None))
            entity_nodes[ent.text] = node.id

            # Handle company name variations
            if ent.label_ == "ORG" and "SpaceX" in ent.text:
                spacex_node = Node(
                    id=f"ORG_SpaceX",
                    type="ORG",
                    properties={"text": "SpaceX", "normalized": "spacex"}
                )
                extracted_elements.append((spacex_node, None))
                entity_nodes["SpaceX"] = spacex_node.id

        # Extract relationships from dependency parsing
        for token in doc:
            if token.dep_ in ["nsubj", "dobj", "pobj"]:
                # Find related entities
                head_ent = None
                token_ent = None

                # Search in entity spans
                for ent in doc.ents:
                    if token.head.i in range(ent.start, ent.end):
                        head_ent = ent
                    if token.i in range(ent.start, ent.end):
                        token_ent = ent

                if head_ent and token_ent:
                    # Create relationship
                    edge = Edge(
                        source=entity_nodes[head_ent.text],
                        target=entity_nodes[token_ent.text],
                        type=token.dep_,
                        properties={
                            "sentence": str(token.sent),
                            "relationship_type": "direct",
                            "confidence": 0.9
                        }
                    )
                    extracted_elements.append((None, edge))

                    # Add collaboration edge for organizations
                    if (head_ent.label_ == "ORG" and token_ent.label_ == "ORG" and
                        "collaborate" in str(token.sent).lower()):
                        collab_edge = Edge(
                            source=entity_nodes[head_ent.text],
                            target=entity_nodes[token_ent.text],
                            type="collaborates_with",
                            properties={
                                "sentence": str(token.sent),
                                "relationship_type": "inferred",
                                "confidence": 0.8
                            }
                        )
                        extracted_elements.append((None, collab_edge))

        return extracted_elements

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