from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio
from collections import defaultdict

class Message(BaseModel):
    """Message structure for agent communication"""
    id: str
    sender: str
    receiver: str
    content: Dict[str, Any]
    type: str
    timestamp: datetime = datetime.now()

class CommunicationBus:
    """Handles communication between agents"""

    def __init__(self):
        self._subscribers = defaultdict(list)
        self._message_queue = asyncio.Queue()
        self._message_history: List[Message] = []

    async def send_message(self, message: Message):
        """Send message to specified receiver"""
        await self._message_queue.put(message)
        self._message_history.append(message)

    async def subscribe(self, agent_id: str, callback):
        """Subscribe agent to receive messages"""
        self._subscribers[agent_id].append(callback)

    async def unsubscribe(self, agent_id: str):
        """Unsubscribe agent from messages"""
        self._subscribers.pop(agent_id, None)

    async def start(self):
        """Start message processing loop"""
        while True:
            message = await self._message_queue.get()

            # Process message
            receivers = self._subscribers.get(message.receiver, [])
            for callback in receivers:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Error processing message: {str(e)}")

            self._message_queue.task_done()

    def get_message_history(self, agent_id: Optional[str] = None) -> List[Message]:
        """Get message history for specific agent"""
        if agent_id:
            return [
                msg for msg in self._message_history 
                if msg.sender == agent_id or msg.receiver == agent_id
            ]
        return self._message_history