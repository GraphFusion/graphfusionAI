
"""Team management system for agent collaboration"""

from typing import Dict, Any, Optional, List
from .agent import Agent, Role
from .knowledge_graph import KnowledgeGraph
from .memory import Memory

class Team:
    """Base class for managing agent teams"""
    def __init__(self, name: str, leader: Optional[Agent] = None):
        self.name = name
        self.leader = leader
        self.members: Dict[str, Agent] = {}
        self.shared_memory = Memory()
        self.knowledge_graph = KnowledgeGraph()
        
    def add_member(self, role: str, agent: Agent):
        """Add a team member with specific role"""
        self.members[role] = agent
        if hasattr(agent, '_memory'):
            agent._memory = self.shared_memory
            
    def remove_member(self, role: str):
        """Remove a team member by role"""
        if role in self.members:
            del self.members[role]
            
    def get_member(self, role: str) -> Optional[Agent]:
        """Get team member by role"""
        return self.members.get(role)
        
    def list_members(self) -> List[Dict[str, Any]]:
        """List all team members and their roles"""
        return [
            {"role": role, "agent": agent.name}
            for role, agent in self.members.items()
        ]
        
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all team members"""
        results = {}
        for role, agent in self.members.items():
            try:
                result = await agent.handle_task(message)
                results[role] = result
            except Exception as e:
                results[role] = {"status": "error", "error": str(e)}
        return results
        
    #def share_knowledge(self, knowledge: Dict[str, Any]):
       # """Share knowledge across team members"""
        #self.shared_memory.store(f"shared_{len(self.shared_memory._data)}", knowledge)
        #return True
    def share_knowledge(self, knowledge):
        current_count = self.shared_memory.get_entry_count()
        self.shared_memory.store(f"shared_{current_count}", knowledge)
        return True
