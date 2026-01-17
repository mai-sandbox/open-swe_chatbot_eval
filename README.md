# LangGraph Flask Chatbot

A basic chatbot built with LangGraph that can have conversations and call a simple weather tool. The chatbot is available both as a CLI application and as a Flask web API.

## Features

- **LangGraph Integration**: Uses LangGraph for conversation flow management
- **Weather Tool**: Can provide weather information for any city
- **Dual Interface**: Available as both CLI and web API
- **Flask REST API**: HTTP endpoints for web integration
- **Error Handling**: Comprehensive error handling and validation

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Create .env file with your Anthropic API key
   cp .env .env.local  # or create .env file manually
   ```
   
   Edit the `.env` file and replace the placeholder with your actual Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your-actual-anthropic-api-key-here
   ```

## Usage

### Option 1: CLI Application (Original)

Run the chatbot in command-line mode:

```bash
python chatbot.py
```

Type your messages and press Enter. Type 'quit' to exit.

### Option 2: Flask Web API (New)

#### Starting the Flask Server

```bash
python app.py
```

The server will start on `http://localhost:5000` with the following endpoints:

#### API Endpoints

**Health Check**
```bash
GET /health
```

Example:
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "message": "Flask chatbot server is running"
}
```

**Chat with the Bot**
```bash
POST /chat
Content-Type: application/json

{
  "message": "Your message here"
}
```

Example:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! How are you?"}'
```

Response:
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "status": "success"
}
```

**Weather Example**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather like in New York?"}'
```

Response:
```json
{
  "response": "It's sunny and 75°F in New York!",
  "status": "success"
}
```

## Testing

### Automated Testing

Run the comprehensive test suite to verify all functionality:

```bash
python test_chatbot.py
```

This will test:
- Server health endpoint
- Basic chat functionality
- Weather tool integration
- Error handling and validation

### Manual Testing

You can also test the API manually using curl, Postman, or any HTTP client:

1. **Start the Flask server**: `python app.py`
2. **Test health endpoint**: `curl http://localhost:5000/health`
3. **Test chat endpoint**: `curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message": "Hello!"}'`

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid JSON, missing message field, or empty message
- **404 Not Found**: Invalid endpoint
- **405 Method Not Allowed**: Wrong HTTP method
- **500 Internal Server Error**: Server-side errors (with detailed logging)

Example error response:
```json
{
  "error": "Missing \"message\" field in request",
  "status": "error"
}
```

## Development

### Project Structure

```
.
├── app.py              # Flask web application
├── chatbot.py          # Original CLI chatbot with LangGraph
├── test_chatbot.py     # Test suite for Flask API
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (API keys)
└── README.md          # This file
```

### Adding New Features

1. **New Tools**: Add tools to `chatbot.py` in the `tools` list
2. **New Endpoints**: Add routes to `app.py`
3. **Tests**: Update `test_chatbot.py` with new test cases

## Troubleshooting

**Server won't start**
- Check if port 5000 is available
- Verify all dependencies are installed
- Check the `.env` file has a valid API key

**Chat requests fail**
- Ensure the Anthropic API key is valid and has credits
- Check server logs for detailed error messages
- Verify JSON payload format is correct

**Tests fail**
- Make sure the Flask server is running before running tests
- Check network connectivity to localhost:5000
- Review test output for specific failure details
