"""
Conversation management system
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    """Message in a conversation"""
    role: str  # system, user, assistant
    content: str
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 100):
        self.messages: List[Message] = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str, **metadata):
        """Add a message to the conversation"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata
        )
        self.messages.append(message)
        
        # Trim history if needed
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_history(self, last_n: Optional[int] = None) -> List[Message]:
        """Get conversation history"""
        if last_n:
            return self.messages[-last_n:]
        return self.messages
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
    
    def format_for_llm(self) -> List[Dict[str, str]]:
        """Format conversation history for LLM API"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
