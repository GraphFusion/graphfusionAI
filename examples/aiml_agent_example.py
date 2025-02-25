"""
Example demonstrating AIML-powered agent capabilities
"""

import asyncio
import os
from mas_framework import Agent, Role
from mas_framework.llm import AIMLProvider, PromptTemplate

@Agent.create("TravelAgent",
    role=Role(
        name="travel_agent",
        capabilities=["plan_trip", "recommend_places"],
        description="Agent that helps plan trips and recommends places"
    )
)
class TravelAgent(Agent):
    """Agent for travel planning and recommendations"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up AIML provider
        provider = AIMLProvider(
            api_key="e098f023457f4038b10d83f5d9411d5d",
            base_url="https://api.aimlapi.com/v1"
        )
        self.set_llm_provider(provider)
        
        # Add prompt templates
        self.add_prompt_template(PromptTemplate(
            name="plan_trip",
            template="You are a travel agent. Plan a trip to {destination} with the following preferences: {preferences}",
            description="Template for trip planning"
        ))
        
        self.add_prompt_template(PromptTemplate(
            name="recommend_places",
            template="You are a travel agent. Recommend places to visit in {location} based on these interests: {interests}",
            description="Template for place recommendations"
        ))

    async def _process_task(self, task: dict) -> dict:
        if task["type"] == "plan_trip":
            # Generate trip plan using chat
            messages = [
                {
                    "role": "system",
                    "content": "You are a travel agent. Be descriptive and helpful."
                },
                {
                    "role": "user",
                    "content": self.format_prompt(
                        "plan_trip",
                        destination=task["data"]["destination"],
                        preferences=task["data"]["preferences"]
                    )
                }
            ]
            
            plan = await self.chat(messages=messages)
            return {
                "trip_plan": plan
            }
            
        elif task["type"] == "recommend_places":
            # Get recommendations using chat
            messages = [
                {
                    "role": "system",
                    "content": "You are a travel agent. Be descriptive and helpful."
                },
                {
                    "role": "user",
                    "content": self.format_prompt(
                        "recommend_places",
                        location=task["data"]["location"],
                        interests=task["data"]["interests"]
                    )
                }
            ]
            
            recommendations = await self.chat(messages=messages)
            return {
                "recommendations": recommendations
            }
            
        return {"error": "Unsupported task type"}

async def main():
    # Create agent instance
    agent = TravelAgent()

    # Example trip planning task
    plan_task = {
        "id": "task1",
        "type": "plan_trip",
        "data": {
            "destination": "San Francisco",
            "preferences": "3-day trip, interested in technology and food"
        }
    }

    # Example place recommendation task
    recommend_task = {
        "id": "task2",
        "type": "recommend_places",
        "data": {
            "location": "San Francisco",
            "interests": "Technology, startups, and local cuisine"
        }
    }

    print("\nPlanning trip...")
    plan_result = await agent.handle_task(plan_task)
    print("\nTrip Plan:")
    print(plan_result)

    print("\nGetting recommendations...")
    recommend_result = await agent.handle_task(recommend_task)
    print("\nRecommendations:")
    print(recommend_result)

if __name__ == "__main__":
    asyncio.run(main())
