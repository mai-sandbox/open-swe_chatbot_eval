"""
Flask web server wrapper for the LangGraph chatbot.
Provides a REST API endpoint for chat interactions.
"""

from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from anthropic import AuthenticationError, RateLimitError, APIError

# Load environment variables
load_dotenv()

# Import the compiled chatbot app from chatbot.py
from chatbot import app as chatbot_app

# Create Flask app
app = Flask(__name__)

def check_api_key():
    """Check if ANTHROPIC_API_KEY is configured."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        return False
    return True

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that accepts JSON with a 'message' field
    and returns the chatbot response as JSON.
    """
    try:
        # Check if API key is configured
        if not check_api_key():
            return jsonify({
                'error': 'ANTHROPIC_API_KEY is not configured. Please copy .env.example to .env and add your API key.',
                'status': 'error'
            }), 503  # Service Unavailable
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        user_message = data['message']
        
        if not user_message or not isinstance(user_message, str):
            return jsonify({
                'error': 'Message must be a non-empty string'
            }), 400
        
        # Process message through the LangGraph chatbot
        result = chatbot_app.invoke({"messages": [HumanMessage(content=user_message)]})
        
        # Extract the bot's response
        bot_response = result['messages'][-1].content
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
        
    except AuthenticationError as e:
        return jsonify({
            'error': 'Invalid or missing Anthropic API key. Please check your ANTHROPIC_API_KEY configuration.',
            'status': 'error'
        }), 401  # Unauthorized
        
    except RateLimitError as e:
        return jsonify({
            'error': 'Rate limit exceeded. Please try again later.',
            'status': 'error'
        }), 429  # Too Many Requests
        
    except APIError as e:
        return jsonify({
            'error': f'Anthropic API error: {str(e)}',
            'status': 'error'
        }), 502  # Bad Gateway
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'chatbot-api'
    })

if __name__ == '__main__':
    # Check if ANTHROPIC_API_KEY is set
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Warning: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please copy .env.example to .env and add your API key.")
    
    print("Starting Flask chatbot server...")
    print("Available endpoints:")
    print("  POST /chat - Send a message to the chatbot")
    print("  GET /health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)


