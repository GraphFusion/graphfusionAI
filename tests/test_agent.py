"""Tests for Agent functionality"""

import pytest
from graphfusionai import Agent, Role
from graphfusionai.memory import Memory
from graphfusionai.knowledge_graph import KnowledgeGraph

@pytest.fixture
def test_role():
    return Role(
        name="test_role",
        capabilities=["test", "analyze"],
        description="Test role for unit tests"
    )

@pytest.fixture
def test_agent(test_role):
    return Agent(name="TestAgent", role=test_role)

def test_agent_initialization(test_agent, test_role):
    """Test basic agent initialization"""
    assert test_agent.name == "TestAgent"
    assert test_agent.role == test_role
    assert test_agent.state == {}

def test_agent_tool_registration(test_agent):
    """Test tool registration"""
    @test_agent.tool(name="test_tool", description="A test tool")
    def test_tool(x: int, y: int) -> int:
        return x + y
    
    assert "test_tool" in test_agent._tools
    assert test_agent._tools["test_tool"].name == "test_tool"
    assert test_agent._tools["test_tool"].description == "A test tool"

@pytest.mark.asyncio
async def test_agent_task_handling(test_agent):
    """Test task handling"""
    with pytest.raises(ValueError):
        await test_agent.handle_task({"type": "unknown_task"})

    with pytest.raises(NotImplementedError):
        await test_agent.handle_task({"type": "test"})

def test_agent_state_management(test_agent):
    """Test agent state management"""
    test_agent.update_state({"key": "value"})
    assert test_agent.state["key"] == "value"

    test_agent.update_state({"another_key": 123})
    assert test_agent.state["another_key"] == 123

def test_agent_memory(test_agent):
    """Test agent memory operations"""
    test_agent.remember("test_key", "test_value")
    assert test_agent.recall("test_key") == "test_value"
    assert test_agent.recall("non_existent") is None

@pytest.mark.asyncio
async def test_agent_tool_execution(test_agent):
    """Test tool execution"""
    @test_agent.tool()
    def add(x: int, y: int) -> int:
        return x + y

    result = await test_agent.execute_tool("add", x=1, y=2)
    assert result == 3

    with pytest.raises(ValueError):
        await test_agent.execute_tool("non_existent_tool")
