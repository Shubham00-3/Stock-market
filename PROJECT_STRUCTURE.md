# Project Structure Overview

This document provides a complete overview of the Market Intelligence AI Chatbot project structure.

## Directory Tree

```
mcp-chatbot/
├── chatbot-backend/                  # FastAPI Chatbot Backend Service
│   ├── agent/                        # LangGraph Agent Implementation
│   │   ├── __init__.py              # Agent module exports
│   │   ├── state.py                 # Agent state definition (TypedDict)
│   │   └── graph.py                 # LangGraph workflow with Groq LLM
│   │
│   ├── mcp_client/                   # MCP Client for Tool Server
│   │   ├── __init__.py              # MCP client module exports
│   │   └── client.py                # MCP client wrapper (HTTP/stdio)
│   │
│   ├── utils/                        # Utility Modules
│   │   ├── __init__.py              # Utils module exports
│   │   ├── cache.py                 # Redis-based response caching
│   │   ├── rate_limiter.py          # Token bucket rate limiting
│   │   └── redis_client.py          # Upstash Redis client singleton
│   │
│   ├── .dockerignore                # Docker ignore rules
│   ├── .gitignore                   # Git ignore rules
│   ├── Dockerfile                   # Docker container definition
│   ├── main.py                      # FastAPI application entry point
│   └── requirements.txt             # Python dependencies
│
├── .dockerignore                     # Root Docker ignore rules
├── .env.template                     # Environment variables template
├── .gitignore                        # Root Git ignore rules
├── DEPLOYMENT.md                     # Cloud deployment guide
├── Dockerfile                        # MCP Server Docker container
├── LICENSE                           # MIT License
├── PROJECT_STRUCTURE.md              # This file
├── README.md                         # Main project documentation
├── docker-compose.yml                # Multi-service Docker orchestration
├── example_client.py                 # Python client usage examples
├── mcp_server_remote.py              # FastMCP tool server
├── quick-start.bat                   # Windows quick start script
├── quick-start.sh                    # Unix quick start script
└── requirements.txt                  # MCP Server Python dependencies
```

## File Descriptions

### Root Level Files

#### `mcp_server_remote.py`
**Purpose**: FastMCP server providing financial data tools

**Key Components**:
- 5 async tools using yfinance and NewsAPI:
  - `get_stock_price()` - Real-time stock data
  - `get_market_news()` - Latest financial news
  - `get_stock_history()` - Historical price data
  - `compare_stocks()` - Multi-stock comparison
  - `get_market_summary()` - Major indices overview
- Health check endpoint
- Error handling and logging

**Port**: 8000

#### `requirements.txt` (Root)
Dependencies for MCP Server:
- `mcp` - FastMCP framework
- `yfinance` - Stock market data
- `aiohttp` - Async HTTP client
- `python-dotenv` - Environment variable loading
- `uvicorn` - ASGI server

#### `Dockerfile` (Root)
Container definition for MCP Server:
- Base: `python:3.11-slim`
- Port: 8000
- Entry point: `python mcp_server_remote.py`

#### `docker-compose.yml`
Multi-service orchestration:
- `mcp-server` service on port 8000
- `chatbot-backend` service on port 8080
- Inter-service networking
- Health checks
- Environment variable passing

#### `README.md`
Main documentation covering:
- Architecture overview
- Feature descriptions
- Setup instructions
- API usage examples
- Troubleshooting guide

#### `DEPLOYMENT.md`
Cloud deployment guide for:
- Railway
- Render
- AWS ECS
- Google Cloud Run
- DigitalOcean
- Monitoring and scaling strategies

#### `example_client.py`
Python client demonstrating:
- Standard query requests
- Streaming responses
- Session management
- Error handling

#### `quick-start.sh` / `quick-start.bat`
Interactive setup scripts for:
- Environment file creation
- Docker Compose deployment
- Local development setup
- Health check verification

### Chatbot Backend Files

#### `chatbot-backend/main.py`
**Purpose**: FastAPI application serving user-facing API

**Key Components**:
- Application lifespan management
- CORS middleware
- Rate limiting middleware
- Endpoints:
  - `GET /` - Service info
  - `GET /health` - Health check
  - `POST /query` - Standard chat query
  - `POST /stream` - Streaming chat (SSE)
- Pydantic models for request/response validation

**Port**: 8080

#### `chatbot-backend/agent/state.py`
**Purpose**: LangGraph agent state definition

**Key Components**:
- `AgentState` TypedDict with:
  - `messages`: List of conversation messages
  - `session_id`: Session identifier

#### `chatbot-backend/agent/graph.py`
**Purpose**: LangGraph workflow with Groq LLM

**Key Components**:
- `MarketIntelligenceAgent` class
- Groq LLM initialization (`ChatGroq`)
- Graph nodes:
  - `_agent_node()` - LLM reasoning and tool calling
  - `_tools_node()` - Tool execution with caching
- Graph edges:
  - Conditional routing based on tool calls
- Memory with `MemorySaver()`
- System prompt for market intelligence

#### `chatbot-backend/mcp_client/client.py`
**Purpose**: MCP client wrapper for connecting to tool server

**Key Components**:
- `MCPClientWrapper` class
- Transport support:
  - HTTP (production)
  - stdio (local development)
- Context manager for connection lifecycle
- Tool format conversion for LLM
- Async tool calling

#### `chatbot-backend/utils/redis_client.py`
**Purpose**: Redis connection singleton

**Key Components**:
- `RedisClient` singleton class
- Upstash Redis connection
- Methods: `get()`, `set()`, `delete()`, `incr()`, `expire()`, `ttl()`
- Graceful degradation if Redis unavailable

#### `chatbot-backend/utils/cache.py`
**Purpose**: Response caching layer

**Key Components**:
- `ResponseCache` class
- Key generation with hashing
- TTL-based expiration (default 5 minutes)
- JSON serialization
- Cache hit/miss logging

#### `chatbot-backend/utils/rate_limiter.py`
**Purpose**: Token bucket rate limiting

**Key Components**:
- `TokenBucketRateLimiter` class
- `RateLimitPresets` configurations:
  - NORMAL: 10 req/min + 5 burst
  - STREAMING: 5 req/min + 2 burst
  - GENEROUS: 30 req/min + 10 burst
- Per-endpoint, per-client tracking
- Rate limit info in responses

#### `chatbot-backend/requirements.txt`
Dependencies for Chatbot Backend:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` + `langchain-core` - LLM framework
- `langgraph` - Agent orchestration
- `langchain-groq` - Groq LLM integration
- `mcp` - MCP client
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `redis` + `upstash-redis` - Caching/rate limiting
- `slowapi` - Rate limiting
- `sse-starlette` - Server-sent events

#### `chatbot-backend/Dockerfile`
Container definition for Chatbot Backend:
- Base: `python:3.11-slim`
- Port: 8080
- Entry point: `python main.py`

## Configuration Files

### `.env.template` (Should be copied to `.env`)
```
# MCP Server
NEWS_API_KEY=your_newsapi_key_here

# Chatbot Backend (create chatbot-backend/.env)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192
MCP_TRANSPORT_PROTOCOL=http
MCP_SERVER_URL=http://localhost:8000/mcp
UPSTASH_REDIS_REST_URL=your_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_token
LOG_LEVEL=INFO
```

## Data Flow

### Standard Query Flow

```
1. Client sends POST /query
2. FastAPI receives request
3. Rate limiter checks limits
4. Agent creates initial state
5. Agent node invokes Groq LLM
6. LLM decides to call tools
7. Tools node executes via MCP:
   a. Check cache
   b. If miss, call MCP server
   c. Cache result
8. Tool results return to agent
9. Agent node generates final response
10. Response returned to client
```

### Streaming Query Flow

```
1. Client sends POST /stream
2. FastAPI returns EventSourceResponse
3. Agent streams graph execution
4. Events sent as SSE:
   - session: Session ID
   - message: Updates
   - done: Completion
   - error: Errors
5. Client receives real-time updates
```

## Service Communication

### HTTP Transport (Production)
```
Chatbot Backend → HTTP → MCP Server
     (port 8080)  →      (port 8000)
```

### stdio Transport (Development)
```
Chatbot Backend → subprocess → MCP Server
     (port 8080)  →  spawn   → (process)
```

## Security Features

1. **Rate Limiting**
   - Token bucket algorithm
   - Per-client tracking
   - Configurable limits

2. **CORS**
   - Configurable origins
   - Credential support

3. **Error Handling**
   - Graceful degradation
   - Detailed logging
   - No sensitive data in errors

4. **Environment Variables**
   - Secrets in .env
   - Never committed to Git
   - Docker secrets support

## Scalability Features

1. **Caching**
   - Redis-based
   - TTL configuration
   - Reduces API calls

2. **Stateless Design**
   - Session in Redis
   - Horizontal scaling ready

3. **Health Checks**
   - Both services
   - Used by orchestrators

4. **Resource Efficiency**
   - Connection pooling
   - Async operations
   - Graceful shutdown

## Development Workflow

### Local Development
```bash
# Terminal 1: MCP Server
python mcp_server_remote.py

# Terminal 2: Chatbot Backend
cd chatbot-backend
python main.py
```

### Docker Development
```bash
docker-compose up --build
```

### Production Deployment
See `DEPLOYMENT.md` for cloud platform guides.

## Testing Strategy

### Manual Testing
```bash
# Health checks
curl http://localhost:8080/health
curl http://localhost:8000/health

# Query test
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AAPL stock price?"}'

# Example client
python example_client.py
```

### Automated Testing (Recommended)
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## Monitoring Points

1. **Application Logs**
   - Request/response logging
   - Error tracking
   - Tool execution times

2. **Health Endpoints**
   - Service availability
   - Agent readiness

3. **Redis Metrics**
   - Cache hit rate
   - Rate limit violations

4. **External APIs**
   - Groq API usage
   - NewsAPI quota
   - yfinance reliability

## Performance Optimization

1. **Caching Strategy**
   - 5-minute TTL for financial data
   - Reduces redundant API calls
   - Faster response times

2. **Connection Pooling**
   - HTTP client reuse
   - Redis connection pooling

3. **Async Operations**
   - Non-blocking I/O
   - Concurrent tool execution
   - Efficient resource usage

4. **Response Streaming**
   - Immediate feedback
   - Reduced perceived latency
   - Better UX for long operations

## Extension Points

### Adding New Tools
1. Add tool function to `mcp_server_remote.py`
2. Use `@mcp.tool()` decorator
3. Agent auto-discovers new tools

### Custom Rate Limits
1. Add preset to `RateLimitPresets`
2. Apply in middleware
3. Configure per endpoint

### Additional LLMs
1. Install provider package
2. Update `agent/graph.py`
3. Configure in `.env`

### New Endpoints
1. Add route to `main.py`
2. Create Pydantic models
3. Implement handler function

## Troubleshooting

### Common Issues

**MCP Connection Failed**
- Check `MCP_SERVER_URL`
- Verify MCP server is running
- Check network connectivity

**Redis Unavailable**
- Verify Upstash credentials
- Check network access
- App continues without Redis

**Groq API Errors**
- Validate API key
- Check rate limits
- Monitor quota usage

**Tool Execution Errors**
- Check tool logs in MCP server
- Verify data source APIs
- Validate input parameters

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
```

Check detailed logs:
```bash
# Docker Compose
docker-compose logs -f

# Local
tail -f mcp_server.log
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Follow the existing structure
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

