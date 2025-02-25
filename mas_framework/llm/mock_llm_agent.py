"""
Mock LLM Agent implementation for testing and demonstration purposes.
"""

from typing import Dict, Any, Optional
from mas_framework import Agent, Role, Message
import json
import asyncio

class MockLLMAgent(Agent):
    """Agent that simulates LLM capabilities for testing"""
    
    def __init__(self, name: str, role: Role):
        """
        Initialize Mock LLM Agent.
        
        Args:
            name: Agent name
            role: Agent role
        """
        super().__init__(name=name, role=role)
        
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        """Process task using mock responses"""
        try:
            # Simulate processing delay
            await asyncio.sleep(1)
            
            if task["type"] == "research":
                result = self._mock_research(task["data"])
            elif task["type"] == "analyze":
                result = self._mock_analysis(task["data"])
            else:
                raise ValueError(f"Unsupported task type: {task['type']}")
            
            # Store in agent memory
            self.remember(f"task_{task['id']}", result)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def _mock_research(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock research results"""
        topic = data["topic"]
        focus_areas = data.get("focus_areas", [])
        
        return {
            "topic": topic,
            "findings": [
                {
                    "area": "Overview",
                    "content": f"Comprehensive research findings about {topic}"
                },
                *[{"area": area, "content": f"Detailed analysis of {area}"} 
                  for area in focus_areas]
            ],
            "references": [
                "Mock Academic Paper 2024",
                "Mock Research Journal 2025"
            ]
        }
        
    def _mock_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock analysis results"""
        text = data.get("text", "")
        
        return {
            "summary": "A concise summary of the analyzed text",
            "key_points": [
                "First key point extracted from text",
                "Second key point with important details",
                "Third key point highlighting conclusions"
            ],
            "sentiment": "positive",
            "confidence_score": 0.85
        }
        
    async def handle_message(self, message: Message):
        """Handle incoming messages with mock responses"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "status": "success",
            "response": f"Processed message: {message.content[:50]}..."
        }
