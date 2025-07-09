#!/usr/bin/env python3
"""
Simple test for basic conversation functionality
"""

import sys
import os

def test_basic_setup():
    """Test basic chatbot setup and imports"""
    print("=== Testing Basic Conversation Functionality ===\n")
    print("Testing basic setup...")
    
    try:
        # Test imports
        import chatbot
        from langchain_core.messages import HumanMessage, AIMessage
        print("✓ Chatbot module imported successfully")
        print("✓ Required message types imported")
        
        # Test graph compilation
        app = chatbot.app
        print("✓ Graph app compiled successfully")
        
        # Test tools configuration
        tools = chatbot.tools
        print(f"✓ Tools configured: {[tool.name for tool in tools]}")
        
        # Test weather tool directly
        weather_result = chatbot.get_weather("New York")
        print(f"✓ Weather tool works: {weather_result}")
        
        print("\n=== Basic Setup Tests: PASSED ===")
        print("Note: Full conversation testing requires valid ANTHROPIC_API_KEY in .env")
        print("Current .env contains placeholder key, so actual conversation testing is limited")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in basic setup: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_setup()
    sys.exit(0 if success else 1)

