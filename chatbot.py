"""
Simple LangGraph chatbot with a weather tool.
Has several API bugs that need fixing.
"""

import os
import sys
from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's sunny and 75°F in {city}!"

# Setup model
llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")

tools = [get_weather]
model_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph_builder.add_edge("tools", "chatbot")

app = graph_builder.compile()

if __name__ == "__main__":
    print("Simple Chatbot Started! Ask about weather or chat.")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        result = app.invoke({"messages": [HumanMessage(content=user_input)]})
        print(f"Bot: {result['messages'][-1].content}")









