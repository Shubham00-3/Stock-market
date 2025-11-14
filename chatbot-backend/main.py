"""
FastAPI Chatbot Backend - Main Application
Serves the user-facing API with LangGraph agent powered by Groq LLM
"""
import os
import uuid
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
import uvicorn

from agent.graph import MarketIntelligenceAgent
from utils.rate_limiter import TokenBucketRateLimiter, RateLimitPresets

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[MarketIntelligenceAgent] = None

# Rate limiters
query_rate_limiter = TokenBucketRateLimiter(**RateLimitPresets.NORMAL)
stream_rate_limiter = TokenBucketRateLimiter(**RateLimitPresets.STREAMING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global agent
    
    # Startup
    logger.info("Starting Market Intelligence Chatbot Backend")
    
    try:
        # Get configuration from environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        
        logger.info(f"Initializing agent with model: {groq_model}")
        
        # Initialize agent
        agent = MarketIntelligenceAgent(
            groq_api_key=groq_api_key,
            model=groq_model
        )
        
        await agent.initialize()
        logger.info("Agent initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Market Intelligence Chatbot Backend")
        if agent:
            await agent.cleanup()
        logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Market Intelligence Chatbot API",
    description="AI-powered chatbot for stock market intelligence using Groq LLM and LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to requests."""
    
    # Get client identifier (use IP or session ID)
    client_id = request.client.host if request.client else "unknown"
    
    # Check if this is a rate-limited endpoint
    endpoint = request.url.path
    
    if endpoint == "/query":
        allowed, rate_info = query_rate_limiter.check_rate_limit(client_id, endpoint)
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": rate_info["reset_in"],
                    "limit": rate_info["limit"]
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset_in"]),
                    "Retry-After": str(rate_info["reset_in"])
                }
            )
    
    elif endpoint == "/stream":
        allowed, rate_info = stream_rate_limiter.check_rate_limit(client_id, endpoint)
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": rate_info["reset_in"],
                    "limit": rate_info["limit"]
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset_in"]),
                    "Retry-After": str(rate_info["reset_in"])
                }
            )
    
    # Process request
    response = await call_next(request)
    
    return response


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for chat queries."""
    
    message: str = Field(..., description="User message/query", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class QueryResponse(BaseModel):
    """Response model for chat queries."""
    
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    tools_used: list[str] = Field(default_factory=list, description="List of tools used")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    service: str
    agent_ready: bool


# Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "service": "Market Intelligence Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "stream": "/stream"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Market Intelligence Chatbot Backend",
        "agent_ready": agent is not None
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process a user query and return the response.
    
    Args:
        request: Query request with message and optional session_id
        
    Returns:
        Agent response with session_id and tools used
    """
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )
    
    try:
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing query for session {session_id}: {request.message[:100]}")
        
        # Invoke agent
        response_text, tools_used = await agent.invoke(request.message, session_id)
        
        logger.info(f"Query completed. Tools used: {tools_used}")
        
        return QueryResponse(
            response=response_text,
            session_id=session_id,
            tools_used=tools_used
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/stream")
async def stream(request: QueryRequest):
    """
    Stream agent responses in real-time using Server-Sent Events.
    
    Args:
        request: Query request with message and optional session_id
        
    Returns:
        EventSourceResponse with streaming updates
    """
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )
    
    try:
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Starting stream for session {session_id}: {request.message[:100]}")
        
        async def event_generator():
            """Generate SSE events from agent stream."""
            try:
                # Send session ID first
                yield {
                    "event": "session",
                    "data": json.dumps({"session_id": session_id})
                }
                
                # Stream agent responses
                async for event in agent.stream(request.message, session_id):
                    # Format event for SSE
                    event_data = {
                        "type": "update",
                        "content": event
                    }
                    
                    yield {
                        "event": "message",
                        "data": json.dumps(event_data)
                    }
                
                # Send completion event
                yield {
                    "event": "done",
                    "data": json.dumps({"status": "completed"})
                }
                
                logger.info(f"Stream completed for session {session_id}")
                
            except Exception as e:
                logger.error(f"Error in stream generator: {str(e)}")
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)})
                }
        
        return EventSourceResponse(event_generator())
        
    except Exception as e:
        logger.error(f"Error starting stream: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting stream: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

