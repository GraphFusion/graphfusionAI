"""
Example demonstrating LLM-powered agent capabilities
"""

import asyncio
import os
from graphfusionai import Agent, Role
from graphfusionai.llm import OpenAIProvider, PromptTemplate

@Agent.create("Researcher",
    role=Role(
        name="researcher",
        capabilities=["research", "summarize"],
        description="Agent that performs research and summarization"
    )
)
class ResearchAgent(Agent):
    """Agent for performing research and summarization tasks"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up LLM provider
        provider = OpenAIProvider()
        self.set_llm_provider(provider)
        
        # Add prompt templates
        self.add_prompt_template(PromptTemplate(
            name="research",
            template="Research the following topic and provide key insights: {topic}",
            description="Template for research tasks"
        ))
        
        self.add_prompt_template(PromptTemplate(
            name="summarize",
            template="Summarize the following text in a concise manner: {text}",
            description="Template for summarization tasks"
        ))

    async def _process_task(self, task: dict) -> dict:
        if task["type"] == "research":
            # Generate research prompt
            prompt = self.format_prompt("research", topic=task["data"]["topic"])
            
            # Get completion from LLM
            research_result = await self.complete(prompt)
            
            # Store in memory
            self.remember(f"research_{task['id']}", research_result)
            
            return {
                "research": research_result
            }
            
        elif task["type"] == "summarize":
            # Start a conversation for summarization
            self._conversation.add_message("user", task["data"]["text"])
            
            # Generate summary using chat
            summary = await self.chat(
                messages=[{
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise summaries."
                }]
            )
            
            return {
                "summary": summary
            }
            
        return {"error": "Unsupported task type"}

async def main():
    # Create agent instance
    agent = ResearchAgent()

    # Example research task
    research_task = {
        "id": "task1",
        "type": "research",
        "data": {
            "topic": "Knowledge Graphs in AI systems"
        }
    }

    # Example summarization task
    summarize_task = {
        "id": "task2",
        "type": "summarize",
        "data": {
            "text": """
            Knowledge graphs are structured representations of information that show relationships
            between different entities. They are particularly useful in AI systems because they
            provide context and allow for more sophisticated reasoning capabilities. By connecting
            different pieces of information, knowledge graphs enable AI systems to understand
            complex relationships and make more informed decisions.
            """
        }
    }

    print("\nPerforming research task...")
    research_result = await agent.handle_task(research_task)
    print("\nResearch Result:")
    print(research_result)

    print("\nPerforming summarization task...")
    summary_result = await agent.handle_task(summarize_task)
    print("\nSummary Result:")
    print(summary_result)

    # Display conversation history
    print("\nConversation History:")
    for msg in agent._conversation.get_history():
        print(f"{msg.role}: {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
