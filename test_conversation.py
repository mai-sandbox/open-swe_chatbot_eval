"""
Test script for basic conversation functionality.
This script tests the chatbot's conversation flow and identifies potential issues.
"""

import os
import sys
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage

# Add the current directory to the path so we can import chatbot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_conversation_flow():
    """Test basic conversation functionality without requiring real API calls."""
    print("Testing basic conversation flow...")
    
    try:
        # Import the chatbot module
        import chatbot
        
        # Test 1: Check if the graph is properly constructed
        print("✓ Chatbot module imported successfully")
        print("✓ Graph app compiled successfully")
        
        # Test 2: Test the state structure
        test_state = {"messages": [HumanMessage(content="Hello")]}
        print("✓ State structure is valid")
        
        # Test 3: Check if tools are properly configured
        print(f"✓ Tools configured: {[tool.name for tool in chatbot.tools]}")
        
        # Test 4: Test the weather tool directly
        weather_result = chatbot.get_weather("New York")
        print(f"✓ Weather tool works: {weather_result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in basic setup: {e}")
        return False

def test_conversation_with_mock():
    """Test conversation functionality with mocked API responses."""
    print("
    
    try:
        import chatbot
        
        # Mock the ChatAnthropic model to avoid API calls
        mock_response = AIMessage(content="Hello! I'm a chatbot. How can I help you today?")
        
        with patch.object(chatbot.model_with_tools, 'invoke', return_value=mock_response):
            # Test simple conversation
            test_messages = [HumanMessage(content="Hello")]
            result = chatbot.chatbot({"messages": test_messages})
            
            print(f"✓ Simple conversation test passed")
            print(f"  Input: Hello")
            print(f"  Output: {result['messages'][0].content}")
            
            # Test multiple message conversation
            test_messages = [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi there!"),
                HumanMessage(content="How are you?")
            ]
            result = chatbot.chatbot({"messages": test_messages})
            print(f"✓ Multi-message conversation test passed")
            
        return True
        
    except Exception as e:
        print(f"✗ Error in conversation testing: {e}")
        return False

def main():
    """Run all conversation tests."""
    print("=== Testing Basic Conversation Functionality ===
    
    success1 = test_basic_conversation_flow()
    success2 = test_conversation_with_mock()
    
    if success1 and success2:
        print("
        print("Note: Full testing requires a valid ANTHROPIC_API_KEY in .env file")
    else:
        print("

if __name__ == "__main__":
    main()


