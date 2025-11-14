@echo off
REM Market Intelligence Chatbot - Quick Start Script for Windows

echo ========================================
echo Market Intelligence Chatbot Setup
echo ========================================
echo.

REM Check if .env files exist
echo Checking configuration files...

if not exist .env (
    echo Warning: Root .env file not found
    echo Creating .env from template...
    (
        echo # MCP Server Configuration
        echo NEWS_API_KEY=your_newsapi_key_here
        echo LOG_LEVEL=INFO
    ) > .env
    echo Created .env file. Please edit it with your credentials.
)

if not exist chatbot-backend\.env (
    echo Warning: chatbot-backend\.env file not found
    echo Creating chatbot-backend\.env from template...
    (
        echo # Groq API Key
        echo GROQ_API_KEY=your_groq_api_key_here
        echo.
        echo # Groq Model
        echo GROQ_MODEL=llama3-8b-8192
        echo.
        echo # MCP Server Connection
        echo MCP_TRANSPORT_PROTOCOL=http
        echo MCP_SERVER_URL=http://localhost:8000/mcp
        echo.
        echo # Upstash Redis
        echo UPSTASH_REDIS_REST_URL=your_upstash_url
        echo UPSTASH_REDIS_REST_TOKEN=your_upstash_token
        echo.
        echo # Server
        echo PORT=8080
        echo LOG_LEVEL=INFO
    ) > chatbot-backend\.env
    echo Created chatbot-backend\.env file. Please edit it with your credentials.
)

echo.
echo Select deployment method:
echo 1^) Docker Compose (Recommended^)
echo 2^) Local Development (Python virtual environments^)
echo 3^) Exit
echo.
set /p choice="Enter your choice [1-3]: "

if "%choice%"=="1" goto docker
if "%choice%"=="2" goto local
if "%choice%"=="3" goto end
echo Invalid choice
goto end

:docker
echo.
echo ========================================
echo Docker Compose Deployment
echo ========================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed
    echo Please install Docker from https://docs.docker.com/get-docker/
    goto end
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker Compose is not installed
    echo Please install Docker Compose from https://docs.docker.com/compose/install/
    goto end
)

echo Building and starting services...
docker-compose up -d --build

echo.
echo Services started successfully!
echo.
echo Service URLs:
echo   - Chatbot API: http://localhost:8080
echo   - MCP Server: http://localhost:8000
echo.
echo Check logs with: docker-compose logs -f
echo Stop services with: docker-compose down
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

curl -s http://localhost:8080/health >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Chatbot Backend is healthy
) else (
    echo [WARNING] Chatbot Backend not responding yet
)

curl -s http://localhost:8000/health >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] MCP Server is healthy
) else (
    echo [WARNING] MCP Server not responding yet
)

goto test

:local
echo.
echo ========================================
echo Local Development Setup
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    echo Please install Python 3.11+ from https://www.python.org/
    goto end
)

REM Setup MCP Server
echo Setting up MCP Server...
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo Starting MCP Server in background...
start /B python mcp_server_remote.py > mcp_server.log 2>&1

REM Setup Chatbot Backend
echo.
echo Setting up Chatbot Backend...
cd chatbot-backend

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo.
echo Setup complete!
echo.
echo To start the Chatbot Backend, run:
echo   cd chatbot-backend
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo MCP Server is running in background
echo Logs are in: mcp_server.log
echo.

cd ..
goto test

:test
echo.
echo ========================================
echo Quick Test
echo ========================================
echo.
echo You can test the API with:
echo.
echo curl -X POST http://localhost:8080/query ^
echo   -H "Content-Type: application/json" ^
echo   -d "{\"message\": \"What is the current price of Apple stock?\"}"
echo.
echo Or run the example client:
echo python example_client.py
echo.
echo For more information, see README.md
echo.
goto end

:end
pause

