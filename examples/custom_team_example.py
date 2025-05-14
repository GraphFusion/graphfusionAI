"""Example demonstrating custom team implementation""" 

import asyncio
from typing import Dict, Any
from graphfusionai import Agent, Role, Team, Tool

class SpecializedTeam(Team):
    """Custom team implementation with specialized behavior"""
    
    async def execute_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Custom workflow implementation"""
        if "researcher" not in self.members:
            return {"status": "error", "error": "No researcher in team"}
            
        # Execute research
        research_result = await self.members["researcher"].handle_task({
            "type": "research",
            "data": {"topic": task.get("data", {}).get("topic", "unknown")}
        })
        
        if research_result.get("status") == "error":
            return research_result
            
        # Share research results with team
        self.share_knowledge({"research_results": research_result})
        
        # Have each member process the results
        results = await self.broadcast({
            "type": "process",
            "data": {"findings": research_result.get("result", {}).get("findings", "")}
        })
        
        return {
            "status": "success",
            "workflow_results": results
        }

async def research_task(topic: str = "unknown") -> Dict[str, Any]:
    """Research task implementation"""
    return {
        "status": "success",
        "result": {
            "findings": f"Research findings about {topic}"
        }
    }

async def analyze_task(findings: str = "") -> Dict[str, Any]:
    """Analysis task implementation"""
    return {
        "status": "success",
        "result": {
            "analysis": f"Analysis of {findings}"
        }
    }

async def main():
    # Create a specialized team
    research_team = SpecializedTeam("ResearchTeam")
    
    # Create research tool
    research_tool = Tool(
        name="research",
        description="Conduct research on a topic",
        func=research_task,
        async_handler=True
    )
    
    # Create analysis tool
    analysis_tool = Tool(
        name="process",  # Note: matches the task type in broadcast
        description="Analyze research findings",
        func=analyze_task,
        async_handler=True
    )
    
    # Create and add team members
    researcher = Agent(
        name="Researcher1",
        role=Role(
            name="researcher",
            capabilities=["research"],
            description="Research specialist"
        )
    )
    researcher.register_tool(research_tool)
    
    analyst = Agent(
        name="Analyst1",
        role=Role(
            name="analyst", 
            capabilities=["process"],  # Note: matches the tool name
            description="Data analyst"
        )
    )
    analyst.register_tool(analysis_tool)
    
    # Add members to team
    research_team.add_member("researcher", researcher)
    research_team.add_member("analyst", analyst)
    
    # Execute team workflow
    result = await research_team.execute_workflow({
        "type": "research_task",
        "data": {
            "topic": "AI Teams"
        }
    })
    
    print("Team workflow results:", result)
    print("Team members:", research_team.list_members())

if __name__ == "__main__":
    asyncio.run(main())
