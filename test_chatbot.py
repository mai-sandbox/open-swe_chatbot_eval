#!/usr/bin/env python3
"""
Test script for the Flask chatbot server.
Tests both /health and /chat endpoints to verify functionality.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Server configuration
BASE_URL = "http://localhost:5000"
HEALTH_ENDPOINT = f"{BASE_URL}/health"
CHAT_ENDPOINT = f"{BASE_URL}/chat"


def test_health_endpoint() -> bool:
    """Test the /health endpoint."""
    print("🔍 Testing /health endpoint...")

    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(
                f"❌ Health check failed with status {response.status_code}: {response.text}"
            )
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the Flask server running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_chat_endpoint(message: str, expected_keywords: list = None) -> bool:
    """Test the /chat endpoint with a specific message."""
    print(f"🔍 Testing /chat endpoint with message: '{message}'")

    try:
        payload = {"message": message}
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            CHAT_ENDPOINT, json=payload, headers=headers, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "")
            status = data.get("status", "")

            print(f"✅ Chat response received:")
            print(f"   Status: {status}")
            print(f"   Response: {bot_response}")

            # Check for expected keywords if provided
            if expected_keywords:
                found_keywords = [
                    kw for kw in expected_keywords if kw.lower() in bot_response.lower()
                ]
                if found_keywords:
                    print(f"   Found expected keywords: {found_keywords}")
                else:
                    print(f"   ⚠️  Expected keywords not found: {expected_keywords}")

            return True
        else:
            print(
                f"❌ Chat request failed with status {response.status_code}: {response.text}"
            )
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the Flask server running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out - chatbot may be taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_chat_error_cases() -> bool:
    """Test error handling in the /chat endpoint."""
    print("🔍 Testing /chat endpoint error handling...")

    test_cases = [
        {"name": "Empty JSON", "payload": {}, "expected_status": 400},
        {
            "name": "Missing message field",
            "payload": {"text": "hello"},
            "expected_status": 400,
        },
        {"name": "Empty message", "payload": {"message": ""}, "expected_status": 400},
        {
            "name": "Non-string message",
            "payload": {"message": 123},
            "expected_status": 400,
        },
    ]

    all_passed = True

    for test_case in test_cases:
        print(f"  Testing: {test_case['name']}")

        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                CHAT_ENDPOINT, json=test_case["payload"], headers=headers, timeout=10
            )

            if response.status_code == test_case["expected_status"]:
                data = response.json()
                print(
                    f"    ✅ Correctly returned {response.status_code}: {data.get('error', 'No error message')}"
                )
            else:
                print(
                    f"    ❌ Expected {test_case['expected_status']}, got {response.status_code}"
                )
                all_passed = False

        except Exception as e:
            print(f"    ❌ Error testing {test_case['name']}: {e}")
            all_passed = False

    return all_passed


def test_weather_functionality() -> bool:
    """Test the weather tool functionality."""
    print("🔍 Testing weather tool functionality...")

    weather_messages = [
        "What's the weather like in New York?",
        "Can you tell me the weather in London?",
        "How's the weather in Tokyo today?",
    ]

    all_passed = True

    for message in weather_messages:
        success = test_chat_endpoint(
            message, expected_keywords=["weather", "sunny", "75°F"]
        )
        if not success:
            all_passed = False
        time.sleep(1)  # Brief pause between requests

    return all_passed


def run_all_tests() -> bool:
    """Run all test cases."""
    print("🚀 Starting Flask chatbot tests...\n")

    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Basic Chat", lambda: test_chat_endpoint("Hello, how are you?")),
        ("Weather Tool", test_weather_functionality),
        ("Error Handling", test_chat_error_cases),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print("=" * 50)

        try:
            result = test_func()
            results.append((test_name, result))

            if result:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")

        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))

        time.sleep(1)  # Brief pause between test suites

    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The Flask chatbot is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the server logs and configuration.")
        return False


def main():
    """Main function to run the tests."""
    print("Flask Chatbot Test Suite")
    print("=" * 50)
    print("Make sure the Flask server is running before starting tests.")
    print("Start the server with: python app.py")
    print("=" * 50)

    # Wait a moment for user to read instructions
    try:
        input("\nPress Enter to start tests (or Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\nTests cancelled.")
        sys.exit(0)

    success = run_all_tests()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
