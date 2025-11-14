#!/bin/bash

# Market Intelligence Chatbot - Quick Start Script
# This script helps you quickly set up and run the application

set -e

echo "========================================"
echo "Market Intelligence Chatbot Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env files exist
echo "Checking configuration files..."

if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: Root .env file not found${NC}"
    echo "Creating .env from template..."
    cat > .env << EOF
# MCP Server Configuration
NEWS_API_KEY=your_newsapi_key_here
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}Created .env file. Please edit it with your credentials.${NC}"
fi

if [ ! -f chatbot-backend/.env ]; then
    echo -e "${YELLOW}Warning: chatbot-backend/.env file not found${NC}"
    echo "Creating chatbot-backend/.env from template..."
    cat > chatbot-backend/.env << EOF
# Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Groq Model
GROQ_MODEL=llama3-8b-8192

# MCP Server Connection
MCP_TRANSPORT_PROTOCOL=http
MCP_SERVER_URL=http://localhost:8000/mcp

# Upstash Redis
UPSTASH_REDIS_REST_URL=your_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_token

# Server
PORT=8080
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}Created chatbot-backend/.env file. Please edit it with your credentials.${NC}"
fi

echo ""
echo "Select deployment method:"
echo "1) Docker Compose (Recommended)"
echo "2) Local Development (Python virtual environments)"
echo "3) Exit"
echo ""
read -p "Enter your choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "========================================"
        echo "Docker Compose Deployment"
        echo "========================================"
        echo ""
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}Error: Docker is not installed${NC}"
            echo "Please install Docker from https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}Error: Docker Compose is not installed${NC}"
            echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
            exit 1
        fi
        
        echo "Building and starting services..."
        docker-compose up -d --build
        
        echo ""
        echo -e "${GREEN}Services started successfully!${NC}"
        echo ""
        echo "Service URLs:"
        echo "  - Chatbot API: http://localhost:8080"
        echo "  - MCP Server: http://localhost:8000"
        echo ""
        echo "Check logs with: docker-compose logs -f"
        echo "Stop services with: docker-compose down"
        echo ""
        echo "Testing health endpoints..."
        sleep 5
        
        if curl -s http://localhost:8080/health > /dev/null; then
            echo -e "${GREEN}✓ Chatbot Backend is healthy${NC}"
        else
            echo -e "${YELLOW}⚠ Chatbot Backend not responding yet (may still be starting)${NC}"
        fi
        
        if curl -s http://localhost:8000/health > /dev/null; then
            echo -e "${GREEN}✓ MCP Server is healthy${NC}"
        else
            echo -e "${YELLOW}⚠ MCP Server not responding yet (may still be starting)${NC}"
        fi
        ;;
        
    2)
        echo ""
        echo "========================================"
        echo "Local Development Setup"
        echo "========================================"
        echo ""
        
        # Check if Python is installed
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}Error: Python 3 is not installed${NC}"
            echo "Please install Python 3.11+ from https://www.python.org/"
            exit 1
        fi
        
        # Setup MCP Server
        echo "Setting up MCP Server..."
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        
        echo "Starting MCP Server in background..."
        nohup python mcp_server_remote.py > mcp_server.log 2>&1 &
        MCP_PID=$!
        echo "MCP Server PID: $MCP_PID"
        
        # Setup Chatbot Backend
        echo ""
        echo "Setting up Chatbot Backend..."
        cd chatbot-backend
        
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        
        echo ""
        echo -e "${GREEN}Setup complete!${NC}"
        echo ""
        echo "To start the Chatbot Backend, run:"
        echo "  cd chatbot-backend"
        echo "  source venv/bin/activate"
        echo "  python main.py"
        echo ""
        echo "MCP Server is running in background (PID: $MCP_PID)"
        echo "Logs are in: mcp_server.log"
        echo ""
        echo "To stop MCP Server:"
        echo "  kill $MCP_PID"
        ;;
        
    3)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Quick Test"
echo "========================================"
echo ""
echo "You can test the API with:"
echo ""
echo "curl -X POST http://localhost:8080/query \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"What is the current price of Apple stock?\"}'"
echo ""
echo "Or run the example client:"
echo "python example_client.py"
echo ""
echo "For more information, see README.md"
echo ""

