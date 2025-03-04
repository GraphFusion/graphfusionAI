"""Specialized agent templates with advanced capabilities"""

from typing import Dict, Any, List, Optional
from .decorators import capability, agent_template, auto_capabilities
from .templates import ResearchAgent
from ..base import Agent
from ..llm import LLMAgent
from ..tools import Tool

@agent_template("data_scientist")
class DataScientistAgent(ResearchAgent):
    """Data science specialist agent"""
    
    @capability("analyze_data", "Analyze datasets and generate insights")
    async def analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.llm_provider.complete(
            f"Analyze this dataset and provide insights: {data}"
        )
        self.memory.store("last_analysis", result)
        return result
        
    @capability("visualize", "Create data visualizations")
    async def visualize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Generate visualization code for: {data}"
        )
        
    @capability("predict", "Make predictions using ML models")
    async def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Make predictions for: {data}"
        )

@agent_template("developer")
class DeveloperAgent(Agent):
    """Software development specialist agent"""
    
    @capability("code_review", "Review and improve code")
    async def code_review(self, code: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Review this code and suggest improvements: {code}"
        )
        
    @capability("debug", "Debug code issues")
    async def debug(self, error: str, code: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Debug this error: {error}\nCode: {code}"
        )
        
    @capability("test", "Generate test cases")
    async def test(self, code: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Generate test cases for: {code}"
        )

@auto_capabilities
class ProductManagerAgent(LLMAgent):
    """Product management specialist agent"""
    
    async def create_roadmap(self, features: List[str]) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Create a product roadmap for: {features}"
        )
        
    async def prioritize(self, items: List[str]) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Prioritize these items: {items}"
        )
        
    async def write_specs(self, feature: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Write specifications for: {feature}"
        )

@agent_template("security")
class SecurityAgent(Agent):
    """Security specialist agent"""
    
    @capability("audit", "Perform security audits")
    async def audit(self, target: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Perform security audit of: {target}"
        )
        
    @capability("scan", "Scan for vulnerabilities")
    async def scan(self, code: str) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Scan for vulnerabilities in: {code}"
        )
        
    @capability("recommend", "Security recommendations")
    async def recommend(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        return await self.llm_provider.complete(
            f"Provide security recommendations for: {findings}"
        )

# Register new templates
SPECIALIZED_TEMPLATES = {
    "data_scientist": {
        "name": "data_scientist",
        "capabilities": [
            "analyze_data",
            "visualize",
            "predict",
            "research",
            "analyze"
        ],
        "description": "Data science and analysis specialist"
    },
    "developer": {
        "name": "developer",
        "capabilities": [
            "code_review",
            "debug",
            "test"
        ],
        "description": "Software development specialist"
    },
    "product_manager": {
        "name": "product_manager",
        "capabilities": [
            "create_roadmap",
            "prioritize",
            "write_specs"
        ],
        "description": "Product management specialist"
    },
    "security": {
        "name": "security",
        "capabilities": [
            "audit",
            "scan",
            "recommend"
        ],
        "description": "Security specialist"
    }
}
