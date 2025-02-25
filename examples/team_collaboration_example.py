"""
Example demonstrating team-based multi-agent collaboration
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from mas_framework import Agent, Role, KnowledgeGraph
from mas_framework.memory import Memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeamLeaderAgent(Agent):
    """Agent responsible for coordinating team activities"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._team_members = {}
        self._knowledge_graph = KnowledgeGraph()
        self._memory = Memory()  # Initialize Memory properly
        self._task_history = []
        
    @property
    def team_members(self):
        return self._team_members
        
    @property
    def task_history(self):
        return self._task_history

    def add_team_member(self, role: str, agent: Agent):
        """Add a team member"""
        self.team_members[role] = agent
        logger.info(f"Added team member: {agent.name} as {role}")

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if task["type"] == "coordinate_research":
            # 1. Assign research task
            researcher = self.team_members.get("researcher")
            if not researcher:
                return {"status": "error", "error": "No researcher available"}

            research_task = {
                "type": "research",
                "data": {"topic": task["data"]["topic"]}
            }
            research_result = await researcher.handle_task(research_task)

            # 2. Assign analysis task
            analyst = self.team_members.get("analyst")
            if analyst and research_result["status"] == "success":
                analysis_task = {
                    "type": "analyze",
                    "data": {"research": research_result["result"]}
                }
                analysis_result = await analyst.handle_task(analysis_task)

                # 3. Assign reporting task
                reporter = self.team_members.get("reporter")
                if reporter and analysis_result["status"] == "success":
                    report_task = {
                        "type": "generate_report",
                        "data": {
                            "research": research_result["result"],
                            "analysis": analysis_result["result"]
                        }
                    }
                    report_result = await reporter.handle_task(report_task)

                    # Store task results in memory and knowledge graph
                    self._store_task_results(task["id"], {
                        "research": research_result,
                        "analysis": analysis_result,
                        "report": report_result
                    })

                    return {
                        "status": "success",
                        "result": {
                            "research": research_result["result"],
                            "analysis": analysis_result["result"],
                            "report": report_result["result"]
                        }
                    }

        return {"status": "error", "error": "Unsupported task type"}

    def _store_task_results(self, task_id: str, results: Dict[str, Any]):
        """Store task results in memory and knowledge graph"""
        # Store in memory
        self._memory.store(f"task_{task_id}", results)

        # Store in task history
        self._task_history.append({
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "results": results
        })

class ResearchAgent(Agent):
    """Agent responsible for gathering information"""

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if task["type"] == "research":
            # Simulate research process
            research_data = {
                "topic": task["data"]["topic"],
                "findings": [
                    f"Finding 1 about {task['data']['topic']}",
                    f"Finding 2 about {task['data']['topic']}",
                    f"Finding 3 about {task['data']['topic']}"
                ],
                "sources": ["Source 1", "Source 2", "Source 3"]
            }

            self.remember(f"research_{task['id']}", research_data)
            return {
                "status": "success",
                "result": research_data
            }
        return {"status": "error", "error": "Unsupported task type"}

class AnalystAgent(Agent):
    """Agent responsible for analyzing information"""

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if task["type"] == "analyze":
            research_data = task["data"]["research"]
            # Simulate analysis process
            analysis = {
                "key_points": [
                    "Key point 1: " + research_data["findings"][0],
                    "Key point 2: " + research_data["findings"][1]
                ],
                "recommendations": [
                    "Recommendation based on finding 1",
                    "Recommendation based on finding 2"
                ]
            }

            self.remember(f"analysis_{task['id']}", analysis)
            return {
                "status": "success",
                "result": analysis
            }
        return {"status": "error", "error": "Unsupported task type"}

class ReporterAgent(Agent):
    """Agent responsible for generating reports"""

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if task["type"] == "generate_report":
            data = task["data"]
            # Generate report combining research and analysis
            report = {
                "title": f"Report on {data['research']['topic']}",
                "summary": "Executive Summary\n" + "\n".join(
                    data['analysis']['key_points']
                ),
                "findings": data['research']['findings'],
                "recommendations": data['analysis']['recommendations'],
                "sources": data['research']['sources'],
                "generated_at": datetime.now().isoformat()
            }

            self.remember(f"report_{task['id']}", report)
            return {
                "status": "success",
                "result": report
            }
        return {"status": "error", "error": "Unsupported task type"}

async def main():
    # Create roles
    leader_role = Role(
        name="team_leader",
        capabilities=["coordinate_research"],
        description="Coordinates team activities and task delegation"
    )

    researcher_role = Role(
        name="researcher",
        capabilities=["research"],
        description="Gathers and compiles information"
    )

    analyst_role = Role(
        name="analyst",
        capabilities=["analyze"],
        description="Analyzes research findings"
    )

    reporter_role = Role(
        name="reporter",
        capabilities=["generate_report"],
        description="Generates comprehensive reports"
    )

    # Create team members
    team_leader = TeamLeaderAgent(
        name="TeamLeader1",
        role=leader_role
    )

    researcher = ResearchAgent(
        name="Researcher1",
        role=researcher_role
    )

    analyst = AnalystAgent(
        name="Analyst1",
        role=analyst_role
    )

    reporter = ReporterAgent(
        name="Reporter1",
        role=reporter_role
    )

    # Build team
    team_leader.add_team_member("researcher", researcher)
    team_leader.add_team_member("analyst", analyst)
    team_leader.add_team_member("reporter", reporter)

    # Create research task
    task = {
        "id": "task1",
        "type": "coordinate_research",
        "data": {
            "topic": "Multi-Agent Systems in AI"
        }
    }

    # Execute team workflow
    try:
        logger.info("\nExecuting team research workflow...")
        result = await team_leader.handle_task(task)

        logger.info("\nWorkflow Results:")
        logger.info(f"Research findings: {result['result']['research']['findings']}")
        logger.info(f"Analysis: {result['result']['analysis']['key_points']}")
        logger.info(f"Report summary: {result['result']['report']['summary']}")

        logger.info("\nTeam Task History:")
        for task_record in team_leader.task_history:
            logger.info(f"Task {task_record['task_id']} completed at {task_record['timestamp']}")

    except Exception as e:
        logger.error(f"Error in team workflow: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())