"""
Simple LangGraph chatbot with a weather tool.
Has several API bugs that need fixing.
"""

from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# Define state
class State(TypedDict):
    # BUG 1: Wrong annotation - should be list, not Sequence
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's sunny and 75°F in {city}!"

# Setup model
model = ChatAnthropic(model="claude-3-haiku-20240307")

# BUG 2: Wrong method name - should be bind_tools
tools = [get_weather]
model_with_tools = model.bind_tool(tools)

def chatbot(state: State):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

# BUG 3: Wrong import - should be StateGraph
graph_builder = WorkflowGraph(State)

graph_builder.add_node("chatbot", chatbot)

# BUG 4: Wrong ToolNode creation - should just pass tools
tool_node = ToolNode(tools_list=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")

# BUG 5: Should use tools_condition from langgraph.prebuilt
graph_builder.add_conditional_edge(
    "chatbot",
    lambda state: "tools" if state["messages"][-1].tool_calls else END,
    {"tools": "tools"}
)

graph_builder.add_edge("tools", "chatbot")

# BUG 6: Wrong method name - should be compile()
app = graph_builder.build()

if __name__ == "__main__":
    print("Simple Chatbot Started! Ask about weather or chat.")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        # BUG 7: Wrong message type - should be HumanMessage
        result = app.invoke({"messages": [AIMessage(content=user_input)]})
        print(f"Bot: {result['messages'][-1].content}")