"""Example demonstrating the new agent factory system"""

import asyncio
from graphfusionai.agents.factory import AgentFactory, AgentConfig

async def main():
    # Create factory
    factory = AgentFactory()
    
    # Method 1: Create from template with config
    researcher = factory.create_agent(
        "researcher",
        AgentConfig(
            name="Researcher1",
            capabilities=["research", "analyze"],
            llm_config={"model": "gpt-4"}
        )
    )
    
    # Method 2: Quick creation with easy_agent
    assistant = AgentFactory.easy_agent(
        name="Assistant1",
        capabilities=["chat", "help"],
        template="assistant"
    )
    
    # Method 3: Create executor with memory config
    executor = factory.create_agent(
        "executor",
        AgentConfig(
            name="Executor1",
            capabilities=["execute", "monitor"],
            memory_config={
                "type": "vector",
                "dimension": 1536
            }
        )
    )
    
    # Use the agents
    research_result = await researcher.research("AI Agents")
    print("Research result:", research_result)
    
    chat_result = await assistant.chat("Tell me about AI")
    print("Chat result:", chat_result)
    
    task_result = await executor.execute({
        "id": "task1",
        "type": "process",
        "data": {"input": "test data"}
    })
    print("Task result:", task_result)
    
    # List available templates
    print("\nAvailable templates:", factory.list_templates())

if __name__ == "__main__":
    asyncio.run(main())
