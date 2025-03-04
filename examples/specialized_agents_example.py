"""Example demonstrating specialized agents and decorator usage"""

import asyncio
from graphfusionai.agents.factory import AgentFactory, AgentConfig
from graphfusionai.agents.specialized import (
    DataScientistAgent,
    DeveloperAgent,
    ProductManagerAgent,
    SecurityAgent
)

async def main():
    # Create specialized agents
    data_scientist = DataScientistAgent(
        name="DataScientist1",
        llm_config={"model": "gpt-4"}
    )
    
    developer = DeveloperAgent(
        name="Developer1",
        llm_config={"model": "gpt-4"}
    )
    
    # ProductManagerAgent uses auto_capabilities
    pm = ProductManagerAgent(
        name="PM1",
        llm_config={"model": "gpt-4"}
    )
    
    security = SecurityAgent(
        name="Security1",
        llm_config={"model": "gpt-4"}
    )
    
    # Use data scientist capabilities
    data = {"type": "timeseries", "values": [1, 2, 3, 4, 5]}
    analysis = await data_scientist.analyze_data(data)
    print("Data Analysis:", analysis)
    
    # Use developer capabilities
    code = "def add(a, b): return a + b"
    review = await developer.code_review(code)
    print("Code Review:", review)
    
    # Use PM capabilities (auto-registered)
    features = ["AI Agents", "Knowledge Graphs", "Vector Search"]
    roadmap = await pm.create_roadmap(features)
    print("Product Roadmap:", roadmap)
    
    # Use security capabilities
    audit = await security.audit("web_app")
    print("Security Audit:", audit)
    
    # Create using factory
    factory = AgentFactory()
    
    # Create another data scientist with different config
    ds2 = factory.create_agent(
        "data_scientist",
        AgentConfig(
            name="DataScientist2",
            capabilities=["analyze_data", "predict"],
            llm_config={"model": "gpt-4"},
            memory_config={"type": "vector"}
        )
    )
    
    prediction = await ds2.predict(data)
    print("Prediction:", prediction)

if __name__ == "__main__":
    asyncio.run(main())
