"""Team management system for agent collaboration, still a simple implementation for now..."""

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
        
    def share_knowledge(self, knowledge: Dict[str, Any]):
        """Share knowledge across team members"""
        # Generate a unique key for the shared knowledge
        current_count = len(self.shared_memory.entries)
        key = f"shared_{current_count}"
        try:
            self.shared_memory.store(key, knowledge)
            return True
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def cleanup(self):
        """Cleanup team resources"""
        # Cleanup shared memory
        self.shared_memory.clear()
        
        # Cleanup knowledge graph
        self.knowledge_graph.cleanup()
        
        # Cleanup all member agents
        for agent in self.members.values():
            await agent.cleanup()
            
        # Clear members
        self.members.clear()
