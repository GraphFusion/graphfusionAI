
"""Example demonstrating custom team implementation"""

import asyncio
from typing import Dict, Any
from mas_framework import Agent, Role, Team

class SpecializedTeam(Team):
    """Custom team implementation with specialized behavior"""
    
    async def execute_workflow(self, task: Dict[str, Any]):
        """Custom workflow implementation"""
        if "researcher" not in self.members:
            return {"status": "error", "error": "No researcher in team"}
            
        # Execute research
        research_result = await self.members["researcher"].handle_task({
            "type": "research",
            "data": task["data"]
        })
        
        # Share research results with team
        self.share_knowledge({"research_results": research_result})
        
        # Have each member process the results
        results = await self.broadcast({
            "type": "process",
            "data": research_result
        })
        
        return {
            "status": "success",
            "workflow_results": results
        }

async def main():
    # Create a specialized team
    research_team = SpecializedTeam("ResearchTeam")
    
    # Create and add team members
    researcher = Agent(
        name="Researcher1",
        role=Role(
            name="researcher",
            capabilities=["research"],
            description="Research specialist"
        )
    )
    
    analyst = Agent(
        name="Analyst1",
        role=Role(
            name="analyst", 
            capabilities=["analyze"],
            description="Data analyst"
        )
    )
    
    # Add members to team
    research_team.add_member("researcher", researcher)
    research_team.add_member("analyst", analyst)
    
    # Execute team workflow
    result = await research_team.execute_workflow({
        "type": "research_task",
        "data": {"topic": "AI Teams"}
    })
    
    print("Team workflow results:", result)
    print("Team members:", research_team.list_members())

if __name__ == "__main__":
    asyncio.run(main())
