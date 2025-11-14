FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server script
COPY mcp_server_remote.py .

# Railway auto-detects the port from the app
# No EXPOSE needed - will use PORT environment variable

# Run the server
CMD ["python", "-u", "mcp_server_remote.py"]

