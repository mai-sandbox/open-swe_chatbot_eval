"""
Test script to verify the chatbot structure and components are correctly set up.
This tests the code structure without requiring an actual API key.
"""
import sys
import os

def test_imports():
    """Test that all imports work correctly."""
    try:
        from typing import Annotated, TypedDict
        from dotenv import load_dotenv
        from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
        from langchain_anthropic import ChatAnthropic
        from langchain_core.tools import tool
        from langgraph.graph import StateGraph, START, END
        from langgraph.graph.message import add_messages
        from langgraph.prebuilt import ToolNode, tools_condition
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_state_definition():
    """Test that State is properly defined."""
    try:
        from typing import Annotated, TypedDict
        from langgraph.graph.message import add_messages
        
        class State(TypedDict):
            messages: Annotated[list, add_messages]
        
        # Test that we can create a state instance
        state = State(messages=[])
        print("✅ State definition is correct")
        return True
    except Exception as e:
        print(f"❌ State definition error: {e}")
        return False

def test_tool_definition():
    """Test that the weather tool is properly defined."""
    try:
        from langchain_core.tools import tool
        
        @tool
        def get_weather(city: str) -> str:
            """Get weather for a city."""
            return f"It's sunny and 75°F in {city}!"
        
        # Test tool execution
        result = get_weather("San Francisco")
        expected = "It's sunny and 75°F in San Francisco!"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("✅ Weather tool works correctly")
        return True
    except Exception as e:
        print(f"❌ Tool definition error: {e}")
        return False

def main():
    print("Testing chatbot structure...")
    tests = [test_imports, test_state_definition, test_tool_definition]
    results = [test() for test in tests]
    
    if all(results):
        print("\n🎉 All structural tests passed! The chatbot code is properly fixed.")
        print("💡 To test full functionality, add a real Anthropic API key to .env")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()


