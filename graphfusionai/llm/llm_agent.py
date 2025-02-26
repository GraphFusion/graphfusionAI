"""
LLM Agent implementation using OpenAI's API for enhanced intelligence.
"""

import json
from typing import Dict, Any, Optional
from graphfusionai import Agent, Role, Message
from openai import OpenAI
import os

class LLMAgent(Agent):
    """Agent that uses OpenAI's API for processing tasks"""
    
    def __init__(self, name: str, role: Role, model: str = "gpt-4o"):
        """
        Initialize LLM Agent.
        
        Args:
            name: Agent name
            role: Agent role
            model: OpenAI model to use (default: gpt-4o)
        """
        super().__init__(name=name, role=role)
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def _process_task(self, task: Dict[str, Any]) -> Any:
        """Process task using OpenAI's API"""
        try:
            # Create system message based on role
            system_msg = {
                "role": "system",
                "content": f"You are an AI agent with the role of {self.role.name}. "
                          f"Your capabilities include: {', '.join(self.role.capabilities)}. "
                          f"Description: {self.role.description}"
            }
            
            # Create user message from task
            user_msg = {
                "role": "user",
                "content": json.dumps(task)
            }
            
            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[system_msg, user_msg],
                response_format={"type": "json_object"}
            )
            
            # Store in agent memory
            result = json.loads(response.choices[0].message.content)
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
            
    async def handle_message(self, message: Message):
        """Handle incoming messages using LLM capabilities"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Process this message: {message.content}"
                }],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            self.remember(f"msg_{message.id}", result)
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
