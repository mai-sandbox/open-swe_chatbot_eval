"""
Flask server wrapper for the LangGraph chatbot.
Exposes the existing chatbot via REST API endpoints.
"""

from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage
import logging

# Import the existing LangGraph chatbot
from chatbot import app as chatbot_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
flask_app = Flask(__name__)

@flask_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'langraph-chatbot',
        'version': '1.0.0'
    })

@flask_app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint that processes messages through the LangGraph chatbot."""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        user_message = data['message']
        logger.info(f"Received message: {user_message}")
        
        # Process message through LangGraph chatbot
        result = chatbot_app.invoke({
            "messages": [HumanMessage(content=user_message)]
        })
        
        # Extract the response from the last message
        bot_response = result['messages'][-1].content
        logger.info(f"Bot response: {bot_response}")
        
        return jsonify({
            'response': bot_response
        })
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@flask_app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/health', '/chat']
    }), 404

@flask_app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Flask chatbot server...")
    flask_app.run(host='0.0.0.0', port=5001, debug=True)

