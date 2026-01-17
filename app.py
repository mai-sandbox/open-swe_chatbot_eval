"""
Flask web application that wraps the existing LangGraph chatbot.
Provides REST API endpoints for chat interaction.
"""

from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage
import traceback
import logging

# Import the existing chatbot app
from chatbot import app as langgraph_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
flask_app = Flask(__name__)

@flask_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server status."""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask chatbot server is running',
        'version': '1.0.0'
    })

@flask_app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that accepts JSON with 'message' field and returns bot's reply.
    
    Expected JSON format:
    {
        "message": "Your message here"
    }
    
    Returns JSON format:
    {
        "response": "Bot's response here",
        "status": "success"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        if 'message' not in data:
            return jsonify({
                'error': 'Missing "message" field in JSON data',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        
        if not user_message or not isinstance(user_message, str):
            return jsonify({
                'error': 'Message must be a non-empty string',
                'status': 'error'
            }), 400
        
        logger.info(f"Received message: {user_message}")
        
        # Invoke the LangGraph chatbot
        result = langgraph_app.invoke({
            "messages": [HumanMessage(content=user_message)]
        })
        
        # Extract the bot's response
        if 'messages' in result and result['messages']:
            bot_response = result['messages'][-1].content
        else:
            bot_response = "I'm sorry, I couldn't generate a response."
        
        logger.info(f"Bot response: {bot_response}")
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@flask_app.route('/', methods=['GET'])
def index():
    """Simple index page with API information."""
    return jsonify({
        'message': 'Flask Chatbot API',
        'endpoints': {
            'GET /health': 'Health check',
            'POST /chat': 'Chat with the bot (requires JSON with "message" field)',
            'GET /': 'This information page'
        },
        'example_usage': {
            'url': '/chat',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': {'message': 'Hello, how are you?'}
        }
    })

if __name__ == '__main__':
    print("Starting Flask chatbot server...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /chat   - Chat with the bot")
    print("  GET  /       - API information")
    
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
