"""Example demonstrating the new easy agent creation patterns"""

from graphfusionai import (
    Agent, Role, Team,
    agent_template, capability, AgentFactory,
    easy_agent
)

# Method 1: Using decorators for capabilities
@capability("research")
@capability("analyze")
class ResearchAgent(Agent):
    async def research(self, topic: str):
        return f"Research results for {topic}"
        
    async def analyze(self, data: str):
        return f"Analysis of {data}"

# Method 2: Using agent templates
@agent_template("researcher")
class QuickResearchAgent(Agent):
    """Agent will automatically get research capabilities"""
    pass

# Method 3: Using the fluent builder pattern
researcher = (Agent.builder()
    .with_name("Researcher1")
    .with_capabilities(["research", "analyze"])
    .with_memory()
    .with_llm("gpt-4")
    .build())

# Method 4: Using the factory pattern
factory = AgentFactory()
analyst = factory.create_agent(
    template="analyst",
    name="Analyst1",
    config={
        "capabilities": ["analyze", "report"],
        "llm_model": "gpt-4"
    }
)

# Method 5: Super easy one-line creation
easy_agent = easy_agent(
    name="EasyAgent1",
    capabilities=["research", "analyze"]
)

async def main():
    # All these methods create fully functional agents
    agents = [
        ResearchAgent(name="Agent1"),
        QuickResearchAgent(name="Agent2"),
        researcher,
        analyst,
        easy_agent
    ]
    
    # They all work with the existing framework
    team = Team("ResearchTeam")
    for i, agent in enumerate(agents):
        team.add_member(f"member{i+1}", agent)
        
    result = await team.execute_workflow({
        "type": "research_task",
        "data": {"topic": "Easy Agent Creation"}
    })
    
    print("Team workflow results:", result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
