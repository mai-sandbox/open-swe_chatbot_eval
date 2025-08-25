"""
Simple LangGraph chatbot with a weather tool.
Has several API bugs that need fixing.
"""

from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv
import re
from datetime import datetime

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
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
model = ChatAnthropic(model="claude-3-haiku-20240307")

tools = [get_weather]
model_with_tools = model.bind_tools(tools)

def input_processor(state: State):
    """
    Validates and preprocesses user input messages.
    Adds metadata like timestamp and message length, and sanitizes input text.
    """
    messages = state["messages"]
    if not messages:
        return {"messages": []}
    
    # Get the last message (should be user input)
    last_message = messages[-1]
    
    # Only process HumanMessage inputs
    if isinstance(last_message, HumanMessage):
        # Sanitize input text - remove excessive whitespace and special characters
        sanitized_content = re.sub(r'\s+', ' ', last_message.content.strip())
        sanitized_content = re.sub(r'[^\w\s\.\?\!\,\-\'\"]', '', sanitized_content)
        
        # Validate input length (limit to 1000 characters)
        if len(sanitized_content) > 1000:
            sanitized_content = sanitized_content[:1000] + "..."
        
        # Add metadata
        timestamp = datetime.now().isoformat()
        message_length = len(sanitized_content)
        
        # Create enhanced message with metadata in additional_kwargs
        enhanced_message = HumanMessage(
            content=sanitized_content,
            additional_kwargs={
                "timestamp": timestamp,
                "message_length": message_length,
                "processed": True
            }
        )
        
        # Replace the last message with the processed one
        processed_messages = messages[:-1] + [enhanced_message]
        return {"messages": processed_messages}
    
    # If not a HumanMessage, return unchanged
    return {"messages": messages}

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









