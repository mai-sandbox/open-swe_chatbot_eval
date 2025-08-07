"""
Flask web application for the LangGraph chatbot.
Provides REST API endpoints for chatbot interaction.
"""

from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage
import logging
import traceback

# Import the compiled LangGraph chatbot
from chatbot import app as chatbot_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
flask_app = Flask(__name__)

@flask_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running."""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask chatbot server is running'
    }), 200

@flask_app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint to interact with the LangGraph chatbot.
    
    Expected JSON payload:
    {
        "message": "Your message here"
    }
    
    Returns:
    {
        "response": "Chatbot response",
        "status": "success"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
            
        if 'message' not in data:
            return jsonify({
                'error': 'Missing "message" field in request',
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
        result = chatbot_app.invoke({"messages": [HumanMessage(content=user_message)]})
        
        # Extract the response from the last message
        bot_response = result['messages'][-1].content
        
        logger.info(f"Bot response: {bot_response}")
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Internal server error occurred while processing your message',
            'status': 'error'
        }), 500

@flask_app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404

@flask_app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'error': 'Method not allowed',
        'status': 'error'
    }), 405

if __name__ == '__main__':
    print("Starting Flask chatbot server...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /chat   - Chat with the bot")
    print("\nExample usage:")
    print('  curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d \'{"message": "Hello!"}\'')
    
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
