from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class OntologyClass(BaseModel):
    """Defines a class in the ontology"""
    name: str
    properties: Dict[str, str] = {}  # property_name: data_type
    parent: Optional[str] = None
    description: str = ""

class Relationship(BaseModel):
    """Defines relationships between ontology classes"""
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = {}

class Ontology:
    """Manages domain ontology"""
    
    def __init__(self):
        self.classes: Dict[str, OntologyClass] = {}
        self.relationships: List[Relationship] = []

    def add_class(self, ontology_class: OntologyClass):
        """Add class to ontology"""
        self.classes[ontology_class.name] = ontology_class

    def add_relationship(self, relationship: Relationship):
        """Add relationship between classes"""
        if relationship.source not in self.classes:
            raise ValueError(f"Source class {relationship.source} not found")
        if relationship.target not in self.classes:
            raise ValueError(f"Target class {relationship.target} not found")
        
        self.relationships.append(relationship)

    def get_class(self, class_name: str) -> Optional[OntologyClass]:
        """Get class definition"""
        return self.classes.get(class_name)

    def get_relationships(self, class_name: str) -> List[Relationship]:
        """Get relationships for a class"""
        return [
            rel for rel in self.relationships 
            if rel.source == class_name or rel.target == class_name
        ]

    def validate_instance(self, class_name: str, instance: Dict[str, Any]) -> bool:
        """Validate instance against class definition"""
        class_def = self.get_class(class_name)
        if not class_def:
            raise ValueError(f"Class {class_name} not found")

        # Validate properties
        for prop_name, prop_type in class_def.properties.items():
            if prop_name not in instance:
                return False
            
            # Basic type checking
            if prop_type == "string" and not isinstance(instance[prop_name], str):
                return False
            elif prop_type == "number" and not isinstance(instance[prop_name], (int, float)):
                return False
            elif prop_type == "boolean" and not isinstance(instance[prop_name], bool):
                return False

        return True

    def export_schema(self) -> Dict[str, Any]:
        """Export ontology schema"""
        return {
            "classes": {
                name: cls.dict() 
                for name, cls in self.classes.items()
            },
            "relationships": [
                rel.dict() for rel in self.relationships
            ]
        }
