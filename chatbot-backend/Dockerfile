FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY . .

# Railway auto-detects the port from the app
# No EXPOSE needed - will use PORT environment variable

# Run the application
CMD ["python", "main.py"]

