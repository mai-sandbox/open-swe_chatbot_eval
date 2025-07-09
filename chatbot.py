"""
Simple LangGraph chatbot with a weather tool.
Has several API bugs that need fixing.
"""

from typing import Annotated, TypedDict
import os
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# Check for required API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY environment variable is not set.")
    print("Please copy .env.example to .env and add your Anthropic API key.")
    exit(1)

# Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's sunny and 75°F in {city}!"

# Setup model
model = ChatAnthropic(model="claude-3-haiku-20240307")

tools = [get_weather]
model_with_tools = model.bind_tools(tools)

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
    
    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'quit':
                break
                
            result = app.invoke({"messages": [HumanMessage(content=user_input)]})
            print(f"Bot: {result['messages'][-1].content}")
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except EOFError:
        print("\n\nGoodbye!")




