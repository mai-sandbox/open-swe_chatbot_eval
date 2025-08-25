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

def response_formatter(state: State):
    """
    Postprocesses AI responses by adding formatting like proper capitalization,
    adding response metadata, and ensuring consistent response structure.
    """
    messages = state["messages"]
    if not messages:
        return {"messages": []}
    
    # Get the last message (should be AI response)
    last_message = messages[-1]
    
    # Only process AIMessage responses
    if isinstance(last_message, AIMessage):
        # Format the response content
        formatted_content = last_message.content
        
        # Ensure proper capitalization - capitalize first letter of sentences
        if formatted_content:
            # Split by sentence endings and capitalize first letter of each sentence
            sentences = re.split(r'([.!?]+\s*)', formatted_content)
            formatted_sentences = []
            
            for i, sentence in enumerate(sentences):
                if i % 2 == 0 and sentence.strip():  # Even indices are actual sentences
                    # Capitalize first letter and ensure proper spacing
                    sentence = sentence.strip()
                    if sentence:
                        sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                    formatted_sentences.append(sentence)
                else:
                    formatted_sentences.append(sentence)
            
            formatted_content = ''.join(formatted_sentences)
            
            # Ensure response ends with proper punctuation
            if formatted_content and not formatted_content[-1] in '.!?':
                formatted_content += '.'
        
        # Add response metadata
        timestamp = datetime.now().isoformat()
        response_length = len(formatted_content)
        word_count = len(formatted_content.split()) if formatted_content else 0
        
        # Create enhanced message with metadata
        enhanced_message = AIMessage(
            content=formatted_content,
            additional_kwargs={
                "timestamp": timestamp,
                "response_length": response_length,
                "word_count": word_count,
                "formatted": True
            }
        )
        
        # Replace the last message with the formatted one
        formatted_messages = messages[:-1] + [enhanced_message]
        return {"messages": formatted_messages}
    
    # If not an AIMessage, return unchanged
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










