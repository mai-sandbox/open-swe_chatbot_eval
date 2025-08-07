"""
Flask web application wrapper for the LangGraph chatbot.
Provides HTTP endpoints for chatbot interaction while maintaining existing functionality.
"""

from flask import Flask, request, jsonify, render_template
import os
import traceback
from langchain_core.messages import HumanMessage

# Import the existing chatbot components
from chatbot import app as langgraph_app

# Initialize Flask app
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@flask_app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages via POST requests.
    Expects JSON with 'message' field, returns JSON with 'response' field.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Invalid request. Expected JSON with "message" field.'
            }), 400
        
        user_message = data['message']
        
        if not user_message or not user_message.strip():
            return jsonify({
                'error': 'Message cannot be empty.'
            }), 400
        
        # Invoke the LangGraph chatbot
        result = langgraph_app.invoke({
            "messages": [HumanMessage(content=user_message.strip())]
        })
        
        # Extract the bot's response
        bot_response = result['messages'][-1].content
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
        
    except Exception as e:
        # Handle any errors gracefully
        error_message = str(e)
        
        # Check for common API key issues
        if ('anthropic' in error_message.lower() or 
            'api' in error_message.lower() or 
            'authentication' in error_message.lower() or
            'unauthorized' in error_message.lower() or
            'api_key' in error_message.lower()):
            error_message = ("API configuration error. Please ensure your ANTHROPIC_API_KEY is set correctly. "
                           "Copy .env.example to .env and add your API key, or set the environment variable directly.")
        
        return jsonify({
            'error': error_message,
            'status': 'error',
            'help': 'Check server logs for more details'
        }), 500

@flask_app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'LangGraph Flask Chatbot'
    })

@flask_app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404

@flask_app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    # Check for API key configuration
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set.")
        print("The chatbot may not function properly without proper API key configuration.")
        print("Please create a .env file with your API key or set the environment variable.")
    
    print("Starting Flask chatbot server...")
    print("Available endpoints:")
    print("  GET  /          - Chat interface")
    print("  POST /chat      - Chat API endpoint")
    print("  GET  /health    - Health check")
    
    # Run Flask development server
    flask_app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

