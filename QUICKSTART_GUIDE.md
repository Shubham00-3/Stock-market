# Quick Start Guide

Get your Market Intelligence AI Chatbot up and running in 5 minutes!

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] Python 3.11 or higher installed
- [ ] Docker and Docker Compose (optional, but recommended)
- [ ] Groq API key ([Get it here](https://console.groq.com))
- [ ] NewsAPI key ([Get it here](https://newsapi.org/register))
- [ ] Upstash Redis account ([Get it here](https://upstash.com))

## Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd mcp-chatbot
```

## Step 2: Configure Environment Variables

### Option A: Use the Quick Start Script (Recommended)

**On Unix/Linux/Mac:**
```bash
./quick-start.sh
```

**On Windows:**
```bash
quick-start.bat
```

The script will create `.env` files for you. Just edit them with your actual API keys.

### Option B: Manual Configuration

**Create `.env` in the root directory:**
```env
NEWS_API_KEY=your_newsapi_key_here
LOG_LEVEL=INFO
```

**Create `chatbot-backend/.env`:**
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192
MCP_TRANSPORT_PROTOCOL=http
MCP_SERVER_URL=http://localhost:8000/mcp
UPSTASH_REDIS_REST_URL=your_upstash_redis_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token
PORT=8080
LOG_LEVEL=INFO
```

## Step 3: Choose Your Deployment Method

### Method 1: Docker Compose (Recommended)

**Advantages:**
- ✅ Easiest setup
- ✅ Both services configured automatically
- ✅ Production-ready
- ✅ Easy to scale

**Start the services:**
```bash
docker-compose up -d
```

**Check the logs:**
```bash
docker-compose logs -f
```

**Stop the services:**
```bash
docker-compose down
```

### Method 2: Local Development

**Advantages:**
- ✅ Best for development
- ✅ Easy debugging
- ✅ Fast iteration

**Terminal 1 - Start MCP Server:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python mcp_server_remote.py
```

**Terminal 2 - Start Chatbot Backend:**
```bash
cd chatbot-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

## Step 4: Verify Everything is Running

### Check Health Endpoints

**MCP Server:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Market Intelligence MCP Server",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Chatbot Backend:**
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Market Intelligence Chatbot Backend",
  "agent_ready": true
}
```

## Step 5: Test the Chatbot

### Method 1: Using curl

**Simple query:**
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current price of Apple stock?"
  }'
```

**With session ID:**
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare Apple and Microsoft stocks",
    "session_id": "my-session-123"
  }'
```

### Method 2: Using the Example Client

```bash
python example_client.py
```

This will run several test queries and show you how to use the API.

### Method 3: Using Python Requests

```python
import requests

# Send a query
response = requests.post(
    "http://localhost:8080/query",
    json={"message": "What is Tesla's stock price?"}
)

# Print the response
data = response.json()
print(f"Response: {data['response']}")
print(f"Tools used: {data['tools_used']}")
```

## Example Queries to Try

Here are some queries to test the chatbot:

### Stock Prices
```
"What is the current price of Apple stock?"
"Show me NVIDIA's stock price"
"How is Tesla doing today?"
```

### Market News
```
"What's the latest news about AI companies?"
"Show me recent news about electric vehicle stocks"
"What's happening in the tech sector?"
```

### Historical Data
```
"Show me Apple's performance over the last 3 months"
"What was Microsoft's stock history in the last year?"
"Give me NVIDIA's historical data for 6 months"
```

### Stock Comparison
```
"Compare Apple, Microsoft, and Google"
"Show me a comparison between Tesla and Ford"
"Compare the FAANG stocks"
```

### Market Summary
```
"Give me a market summary"
"How are the major indices doing?"
"What's the status of S&P 500 and NASDAQ?"
```

### Complex Queries
```
"What is Apple's current price and how has it performed over the last 6 months?"
"Compare Tesla and NIO stocks, and show me recent news about electric vehicles"
"Give me a market summary and the latest tech stock news"
```

## Understanding the Response

### Standard Response Format

```json
{
  "response": "Apple (AAPL) is currently trading at $175.50...",
  "session_id": "abc-123-def-456",
  "tools_used": ["get_stock_price"]
}
```

**Fields:**
- `response`: The AI's answer to your query
- `session_id`: Unique session identifier for conversation continuity
- `tools_used`: List of tools the AI used to answer (for transparency)

### Rate Limiting

The API has rate limits to prevent abuse:
- **Query endpoint**: 10 requests/minute + 5 burst
- **Stream endpoint**: 5 requests/minute + 2 burst

If you hit the limit, you'll get a `429` response with retry information.

## Streaming Responses

For real-time responses, use the `/stream` endpoint:

```bash
curl -N -X POST http://localhost:8080/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Give me a detailed market analysis"
  }'
```

You'll receive Server-Sent Events (SSE) with updates as they happen.

## Troubleshooting

### Issue: "Connection refused" when testing

**Solution:**
1. Make sure both services are running
2. Check the logs for errors
3. Verify ports 8000 and 8080 are not in use

**Docker:**
```bash
docker-compose ps
docker-compose logs
```

**Local:**
```bash
# Check if processes are running
ps aux | grep python

# Check if ports are in use
netstat -an | grep 8000
netstat -an | grep 8080
```

### Issue: "Agent not initialized"

**Solution:**
1. Check if Groq API key is correct
2. Verify internet connection
3. Check chatbot-backend logs

```bash
# Docker
docker-compose logs chatbot-backend

# Local
# Check terminal where you ran main.py
```

### Issue: Tools returning errors

**Solution:**
1. Verify NewsAPI key is correct
2. Check stock symbols are valid (use uppercase)
3. Review MCP server logs

```bash
# Docker
docker-compose logs mcp-server

# Local
# Check terminal where you ran mcp_server_remote.py
```

### Issue: Redis connection failed

**Solution:**
The app will still work without Redis (caching and rate limiting will be disabled):
1. Verify Upstash credentials
2. Check internet connection to Upstash
3. The app logs warnings but continues

### Issue: Rate limit exceeded

**Solution:**
1. Wait for the rate limit to reset (shown in error message)
2. Use session IDs to continue conversations
3. Consider upgrading rate limits if needed

## Next Steps

Now that you have the chatbot running:

1. **Explore the API** - Try different queries and see what the AI can do
2. **Build a frontend** - Use the API to create a web or mobile interface
3. **Customize the agent** - Modify the system prompt in `agent/graph.py`
4. **Add more tools** - Extend the MCP server with additional financial data sources
5. **Deploy to production** - See `DEPLOYMENT.md` for cloud deployment guides

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

These provide interactive API documentation.

## Useful Commands

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build

# View service status
docker-compose ps
```

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate          # Unix/Mac
venv\Scripts\activate              # Windows

# Deactivate virtual environment
deactivate

# Install dependencies
pip install -r requirements.txt

# Run with debug logging
export LOG_LEVEL=DEBUG             # Unix/Mac
set LOG_LEVEL=DEBUG                # Windows
```

## Getting Help

If you run into issues:

1. **Check the logs** - Most errors are explained in the logs
2. **Read the README** - Comprehensive documentation
3. **Review troubleshooting** - Common issues and solutions
4. **Open an issue** - Report bugs on GitHub
5. **Check examples** - See `example_client.py`

## Resources

- **README.md** - Full project documentation
- **DEPLOYMENT.md** - Cloud deployment guides
- **PROJECT_STRUCTURE.md** - Code organization
- **API Docs** - http://localhost:8080/docs

## Support

- GitHub Issues: Report bugs or request features
- Documentation: Check README.md and other guides
- Examples: See example_client.py

---

**Congratulations!** 🎉 You now have a fully functional Market Intelligence AI Chatbot running!

