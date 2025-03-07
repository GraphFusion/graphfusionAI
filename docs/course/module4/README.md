# Module 4: Multi-Agent Systems

## Learning Objectives
By the end of this module, you will:
- Design and implement multi-agent architectures
- Master inter-agent communication patterns
- Create collaborative problem-solving systems
- Handle agent coordination and conflict resolution

## 1. Multi-Agent Architecture

### Agent Network Setup
```python
from graphfusionai import AgentNetwork, Agent, Role, CommunicationBus
from typing import Dict, Any, List

class AgentNetwork:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.comm_bus = CommunicationBus()

    async def add_agent(self, agent: Agent):
        self.agents[agent.id] = agent
        await self.comm_bus.register_agent(agent)

    async def remove_agent(self, agent_id: str):
        if agent_id in self.agents:
            await self.comm_bus.unregister_agent(agent_id)
            del self.agents[agent_id]

    async def broadcast(self, message: Dict[str, Any]):
        await self.comm_bus.broadcast(message)
```

## 2. Inter-Agent Communication

### Message Passing System
```python
from graphfusionai import Message, MessageType, MessagePriority

class CommunicativeAgent(Agent):
    async def send_message(
        self,
        recipient_id: str,
        content: Dict[str, Any],
        msg_type: MessageType = MessageType.TASK,
        priority: MessagePriority = MessagePriority.NORMAL
    ):
        message = Message(
            sender_id=self.id,
            recipient_id=recipient_id,
            content=content,
            type=msg_type,
            priority=priority
        )
        await self.comm_bus.send_message(message)

    async def handle_message(self, message: Message):
        if message.type == MessageType.TASK:
            result = await self._process_task(message.content)
            await self.send_message(
                message.sender_id,
                {"result": result},
                MessageType.RESPONSE
            )
        elif message.type == MessageType.QUERY:
            response = await self._handle_query(message.content)
            await self.send_message(
                message.sender_id,
                response,
                MessageType.RESPONSE
            )
```

## 3. Collaborative Problem Solving

### Task Distribution System
```python
class TaskManager(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.task_queue = []
        self.agent_capabilities = {}

    async def register_agent_capabilities(
        self,
        agent_id: str,
        capabilities: List[str]
    ):
        self.agent_capabilities[agent_id] = capabilities

    async def submit_task(self, task: Dict[str, Any]):
        required_capability = task.get("required_capability")
        suitable_agents = [
            agent_id for agent_id, caps in self.agent_capabilities.items()
            if required_capability in caps
        ]

        if not suitable_agents:
            raise ValueError(f"No agent found with capability: {required_capability}")

        # Simple round-robin distribution
        selected_agent = suitable_agents[len(self.task_queue) % len(suitable_agents)]
        
        await self.send_message(
            selected_agent,
            task,
            MessageType.TASK
        )
        self.task_queue.append({
            "task": task,
            "assigned_to": selected_agent,
            "status": "assigned"
        })
```

## 4. Conflict Resolution

### Consensus Building
```python
class ConsensusAgent(Agent):
    def __init__(self, name: str, role: Role):
        super().__init__(name=name, role=role)
        self.proposals = {}
        self.votes = {}

    async def propose_solution(
        self,
        problem_id: str,
        solution: Any
    ):
        proposal = {
            "problem_id": problem_id,
            "solution": solution,
            "proposer": self.id,
            "timestamp": datetime.now()
        }
        
        await self.comm_bus.broadcast({
            "type": "PROPOSAL",
            "content": proposal
        })
        
        self.proposals[problem_id] = proposal

    async def vote_on_proposal(
        self,
        problem_id: str,
        proposal_id: str,
        vote: bool
    ):
        if problem_id not in self.votes:
            self.votes[problem_id] = {}
            
        self.votes[problem_id][self.id] = {
            "vote": vote,
            "timestamp": datetime.now()
        }

        # Check if consensus is reached
        votes = self.votes[problem_id]
        total_votes = len(votes)
        positive_votes = sum(1 for v in votes.values() if v["vote"])
        
        if total_votes >= len(self.agent_network.agents) * 0.67:  # 2/3 majority
            consensus_reached = positive_votes / total_votes > 0.5
            if consensus_reached:
                await self.comm_bus.broadcast({
                    "type": "CONSENSUS_REACHED",
                    "content": {
                        "problem_id": problem_id,
                        "proposal": self.proposals[problem_id],
                        "votes": votes
                    }
                })
```

## Exercise: Build a Distributed Task Processing System

Create a system with multiple specialized agents:
1. A TaskManager agent that distributes tasks
2. Multiple Worker agents with different capabilities
3. A Supervisor agent that monitors progress
4. A Consensus agent for handling conflicts

Requirements:
- Implement load balancing
- Handle agent failures gracefully
- Monitor system performance
- Implement conflict resolution
- Add logging and monitoring

## Next Steps
- Check the [exercise solution](exercise_solution.py)
- Review the [API Reference](../../api_reference.md)
- Continue to [Module 5](../module5/README.md) for real-world applications
