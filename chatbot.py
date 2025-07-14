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

# Validate required environment variables
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY environment variable is required.")
    print("Please set your Anthropic API key in a .env file or as an environment variable.")
    print("Example: ANTHROPIC_API_KEY=your_api_key_here")
    sys.exit(1)

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
    try:
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    except Exception as e:
        # Create an error message that the user will see
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content=error_msg)]}

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
        
        try:
            print("Bot: ", end="", flush=True)
            
            # Use streaming for better user experience
            response_content = ""
            for chunk in app.stream({"messages": [HumanMessage(content=user_input)]}):
                if "chatbot" in chunk:
                    if chunk["chatbot"]["messages"]:
                        content = chunk["chatbot"]["messages"][-1].content
                        if content != response_content:
                            print(content[len(response_content):], end="", flush=True)
                            response_content = content
            
            print()  # New line after streaming response
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please try again or type 'quit' to exit.")













