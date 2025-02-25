"""
Prompt management system
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
from pathlib import Path

class PromptTemplate(BaseModel):
    """Template for prompts with variables"""
    name: str
    template: str
    description: Optional[str] = None
    
    def format(self, **kwargs) -> str:
        """Format template with given variables"""
        return self.template.format(**kwargs)

class PromptManager:
    """Manages prompt templates and their loading/saving"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        self.templates: Dict[str, PromptTemplate] = {}
        self.templates_dir = Path(templates_dir) if templates_dir else None
        if self.templates_dir and self.templates_dir.exists():
            self.load_templates()
    
    def add_template(self, template: PromptTemplate):
        """Add a new prompt template"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get prompt template by name"""
        return self.templates.get(name)
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with given variables"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        return template.format(**kwargs)
    
    def load_templates(self):
        """Load templates from templates directory"""
        if not self.templates_dir:
            return
            
        for file in self.templates_dir.glob("*.json"):
            with open(file) as f:
                data = json.load(f)
                template = PromptTemplate(**data)
                self.add_template(template)
    
    def save_templates(self):
        """Save templates to templates directory"""
        if not self.templates_dir:
            return
            
        self.templates_dir.mkdir(exist_ok=True)
        for template in self.templates.values():
            file = self.templates_dir / f"{template.name}.json"
            with open(file, "w") as f:
                json.dump(template.dict(), f, indent=2)
