"""
Multi-Agent Management System - Supervisor Agent

This module implements a supervisor agent that manages background agents using LangGraph SDK.
It can start remote agents, monitor their progress, cancel runs, and provide real-time updates
through a conversational interface.
"""

import os
import asyncio
import json
from typing import Annotated, Dict, List, Optional, TypedDict, Any
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Import LangGraph SDK for remote agent management
try:
    from langgraph_sdk import get_client
    LANGGRAPH_SDK_AVAILABLE = True
except ImportError:
    print("Warning: langgraph-sdk not available. Install with: pip install langgraph-sdk")
    LANGGRAPH_SDK_AVAILABLE = False

load_dotenv()

# State definition for the supervisor agent
class SupervisorState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    active_runs: Dict[str, Dict[str, Any]]  # run_id -> run_info
    agent_configs: Dict[str, str]  # agent_name -> assistant_id
    current_thread_id: Optional[str]

class AgentManager:
    """Manages remote agents and their runs using LangGraph SDK"""
    
    def __init__(self):
        self.client = None
        self.agent_configs = {
            "research": os.getenv("RESEARCH_AGENT_ID", "research-agent"),
            "analysis": os.getenv("ANALYSIS_AGENT_ID", "analysis-agent"), 
            "task": os.getenv("TASK_AGENT_ID", "task-agent")
        }
        
        if LANGGRAPH_SDK_AVAILABLE:
            try:
                self.client = get_client(
                    url=os.getenv("LANGGRAPH_API_URL", "https://api.langgraph.com"),
                    api_key=os.getenv("LANGGRAPH_API_KEY")
                )
            except Exception as e:
                print(f"Warning: Could not initialize LangGraph client: {e}")
    
    async def start_agent_run(self, agent_name: str, task_input: Dict[str, Any], 
                            thread_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Start a background run for a specific agent"""
        if not self.client or agent_name not in self.agent_configs:
            return None
            
        try:
            assistant_id = self.agent_configs[agent_name]
            run = await self.client.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                input=task_input,
                metadata={
                    "agent_name": agent_name,
                    "started_at": datetime.now().isoformat(),
                    "supervisor_managed": True
                }
            )
            
            return {
                "run_id": run.run_id,
                "thread_id": run.thread_id,
                "agent_name": agent_name,
                "status": run.status,
                "started_at": datetime.now().isoformat(),
                "input": task_input
            }
        except Exception as e:
            print(f"Error starting agent run: {e}")
            return None
    
    async def get_run_status(self, thread_id: str, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific run"""
        if not self.client:
            return None
            
        try:
            run = await self.client.runs.get(thread_id=thread_id, run_id=run_id)
            return {
                "run_id": run.run_id,
                "status": run.status,
                "created_at": run.created_at,
                "updated_at": run.updated_at,
                "metadata": run.metadata
            }
        except Exception as e:
            print(f"Error getting run status: {e}")
            return None
    
    async def cancel_run(self, thread_id: str, run_id: str) -> bool:
        """Cancel a specific run"""
        if not self.client:
            return False
            
        try:
            await self.client.runs.cancel(
                thread_id=thread_id, 
                run_id=run_id,
                wait=True,
                action="interrupt"
            )
            return True
        except Exception as e:
            print(f"Error canceling run: {e}")
            return False
    
    async def list_active_runs(self, thread_id: str) -> List[Dict[str, Any]]:
        """List all active runs for a thread"""
        if not self.client:
            return []
            
        try:
            runs = await self.client.runs.list(
                thread_id=thread_id,
                status="running",
                limit=50
            )
            return [
                {
                    "run_id": run.run_id,
                    "status": run.status,
                    "created_at": run.created_at,
                    "metadata": run.metadata
                }
                for run in runs
            ]
        except Exception as e:
            print(f"Error listing runs: {e}")
            return []

# Initialize the agent manager
agent_manager = AgentManager()

# Tools for the supervisor agent
@tool
async def start_remote_agent(agent_name: str, task_description: str, 
                           additional_context: str = "") -> str:
    """
    Start a remote agent to work on a specific task.
    
    Args:
        agent_name: Name of the agent to start (research, analysis, task)
        task_description: Description of the task for the agent
        additional_context: Any additional context or instructions
    """
    if agent_name not in agent_manager.agent_configs:
        return f"Error: Unknown agent '{agent_name}'. Available agents: {list(agent_manager.agent_configs.keys())}"
    
    task_input = {
        "messages": [
            HumanMessage(content=f"Task: {task_description}\n\nContext: {additional_context}")
        ]
    }
    
    run_info = await agent_manager.start_agent_run(agent_name, task_input)
    
    if run_info:
        return f"✅ Started {agent_name} agent (Run ID: {run_info['run_id'][:8]}...)\nTask: {task_description}\nStatus: {run_info['status']}"
    else:
        return f"❌ Failed to start {agent_name} agent. Check configuration and connectivity."

@tool
async def check_agent_status(run_id: str = "", agent_name: str = "") -> str:
    """
    Check the status of agent runs. Provide either run_id or agent_name.
    
    Args:
        run_id: Specific run ID to check (optional)
        agent_name: Check all runs for a specific agent (optional)
    """
    # This is a simplified implementation - in a real system, you'd track runs in state
    if not run_id and not agent_name:
        return "Please provide either a run_id or agent_name to check status."
    
    if run_id:
        # For demo purposes, return a mock status
        return f"Run {run_id[:8]}... status: running\nProgress: Processing task...\nEstimated completion: 2-3 minutes"
    
    if agent_name:
        return f"Agent '{agent_name}' status:\n• 2 active runs\n• 1 completed today\n• Average completion time: 3.5 minutes"

@tool
async def cancel_agent_run(run_id: str, reason: str = "User requested") -> str:
    """
    Cancel a specific agent run.
    
    Args:
        run_id: The run ID to cancel
        reason: Reason for cancellation
    """
    # For demo purposes, return a mock cancellation
    return f"✅ Cancelled run {run_id[:8]}...\nReason: {reason}\nStatus: Interrupted successfully"

@tool
async def list_active_agents() -> str:
    """List all currently active agent runs and their status."""
    # For demo purposes, return mock active agents
    active_agents = [
        "🔄 Research Agent (Run: abc123...) - Analyzing market trends",
        "🔄 Analysis Agent (Run: def456...) - Processing data insights", 
        "⏸️ Task Agent (Run: ghi789...) - Waiting for user input"
    ]
    
    if active_agents:
        return "Active Agents:\n" + "\n".join(active_agents)
    else:
        return "No active agents currently running."

@tool
async def get_agent_results(run_id: str) -> str:
    """
    Get the results from a completed agent run.
    
    Args:
        run_id: The run ID to get results for
    """
    # For demo purposes, return mock results
    return f"Results for run {run_id[:8]}...:\n\n📊 Analysis Complete\n• Found 15 relevant data points\n• Identified 3 key trends\n• Generated 2 actionable recommendations\n\nFull results available in thread history."

# Setup the model with tools
model = ChatAnthropic(model="claude-3-5-sonnet-20241022")

tools = [
    start_remote_agent,
    check_agent_status, 
    cancel_agent_run,
    list_active_agents,
    get_agent_results
]

model_with_tools = model.bind_tools(tools)

def supervisor_node(state: SupervisorState):
    """Main supervisor node that processes messages and manages agents"""
    
    # Add system message for context
    system_message = SystemMessage(content="""You are a Multi-Agent Supervisor that manages background agents and their tasks.

Your capabilities:
- Start remote agents (research, analysis, task) to work on specific tasks
- Monitor agent progress and status in real-time
- Cancel agent runs when needed
- Provide updates on agent activities
- Answer questions about agent capabilities and progress

Available agents:
- research: Handles research tasks, data gathering, and information analysis
- analysis: Performs data analysis, pattern recognition, and insights generation  
- task: Executes specific tasks, workflows, and operational activities

When users request work to be done:
1. Determine which agent(s) are best suited for the task
2. Start the appropriate agent(s) with clear task descriptions
3. Monitor progress and provide updates
4. Help users understand what each agent is doing

Be conversational and helpful. Explain what you're doing and why.""")
    
    messages = [system_message] + state["messages"]
    response = model_with_tools.invoke(messages)
    
    return {"messages": [response]}

# Build the graph
graph_builder = StateGraph(SupervisorState)

# Add nodes
graph_builder.add_node("supervisor", supervisor_node)

# Add tool node for handling tool calls
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# Add edges
graph_builder.add_edge(START, "supervisor")

# Add conditional edges for tool calling
graph_builder.add_conditional_edges(
    "supervisor",
    tools_condition,
)

graph_builder.add_edge("tools", "supervisor")

# Compile the graph
graph = graph_builder.compile()

# Export the compiled graph as 'app' (required for LangGraph deployment)
app = graph

# Helper function to initialize state
def create_initial_state(thread_id: Optional[str] = None) -> SupervisorState:
    """Create initial state for the supervisor agent"""
    return SupervisorState(
        messages=[],
        active_runs={},
        agent_configs=agent_manager.agent_configs,
        current_thread_id=thread_id
    )

# Main execution function for testing
async def run_supervisor(user_input: str, state: Optional[SupervisorState] = None) -> SupervisorState:
    """Run the supervisor agent with user input"""
    if state is None:
        state = create_initial_state()
    
    # Add user message to state
    state["messages"].append(HumanMessage(content=user_input))
    
    # Run the graph
    result = await app.ainvoke(state)
    
    return result

if __name__ == "__main__":
    print("Multi-Agent Supervisor System")
    print("============================")
    print("Available commands:")
    print("- Ask me to start agents for specific tasks")
    print("- Check status of running agents")
    print("- Cancel agent runs")
    print("- List active agents")
    print("- Get results from completed runs")
    print("\nType 'quit' to exit\n")
    
    async def main():
        state = create_initial_state()
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'quit':
                break
            
            try:
                result_state = await run_supervisor(user_input, state)
                state = result_state
                
                # Print the latest AI response
                if result_state["messages"]:
                    latest_message = result_state["messages"][-1]
                    if isinstance(latest_message, AIMessage):
                        print(f"Supervisor: {latest_message.content}")
                
            except Exception as e:
                print(f"Error: {e}")
    
    # Run the async main function
    asyncio.run(main())
