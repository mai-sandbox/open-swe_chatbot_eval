"""
Simple LangGraph chatbot with a weather tool.
Has several API bugs that need fixing.
"""
import os

from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
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
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print("Error: ANTHROPIC_API_KEY is not set or is using the placeholder value.")
    print("Please set your Anthropic API key in the .env file.")
    print("You can get an API key from: https://console.anthropic.com/")
    exit(1)

model = ChatAnthropic(model="claude-3-haiku-20240307", api_key=api_key)

tools = [get_weather]
model_with_tools = model.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_conditional_edges("chatbot", tools_condition)

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


