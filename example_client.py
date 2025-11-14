"""
Example client demonstrating how to interact with the Market Intelligence Chatbot API.
"""
import requests
import json
import time
from typing import Optional


class ChatbotClient:
    """Simple client for the Market Intelligence Chatbot API."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the chatbot API
        """
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def query(self, message: str, session_id: Optional[str] = None) -> dict:
        """
        Send a query to the chatbot.
        
        Args:
            message: User message
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Response dictionary
        """
        url = f"{self.base_url}/query"
        
        payload = {
            "message": message,
            "session_id": session_id or self.session_id
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Store session ID for future requests
        if not self.session_id:
            self.session_id = data.get("session_id")
        
        return data
    
    def stream(self, message: str, session_id: Optional[str] = None):
        """
        Stream responses from the chatbot.
        
        Args:
            message: User message
            session_id: Optional session ID for conversation continuity
            
        Yields:
            Response events
        """
        url = f"{self.base_url}/stream"
        
        payload = {
            "message": message,
            "session_id": session_id or self.session_id
        }
        
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                # Parse SSE format
                if line.startswith('event:'):
                    event_type = line.split(':', 1)[1].strip()
                elif line.startswith('data:'):
                    data = line.split(':', 1)[1].strip()
                    try:
                        data_json = json.loads(data)
                        
                        # Store session ID
                        if event_type == 'session':
                            self.session_id = data_json.get('session_id')
                        
                        yield {
                            'event': event_type,
                            'data': data_json
                        }
                    except json.JSONDecodeError:
                        pass
    
    def health(self) -> dict:
        """
        Check API health.
        
        Returns:
            Health status dictionary
        """
        url = f"{self.base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the chatbot client."""
    
    # Initialize client
    client = ChatbotClient("http://localhost:8080")
    
    # Check health
    print("=== Health Check ===")
    health = client.health()
    print(json.dumps(health, indent=2))
    print()
    
    # Example 1: Simple query
    print("=== Example 1: Stock Price Query ===")
    response = client.query("What is the current price of Apple stock?")
    print(f"Response: {response['response']}")
    print(f"Tools Used: {response['tools_used']}")
    print(f"Session ID: {response['session_id']}")
    print()
    
    # Example 2: Follow-up query (using same session)
    print("=== Example 2: Follow-up Query ===")
    response = client.query("How about Microsoft?")
    print(f"Response: {response['response']}")
    print(f"Tools Used: {response['tools_used']}")
    print()
    
    # Example 3: Market news
    print("=== Example 3: Market News ===")
    response = client.query("What's the latest news about AI stocks?")
    print(f"Response: {response['response'][:200]}...")
    print(f"Tools Used: {response['tools_used']}")
    print()
    
    # Example 4: Stock comparison
    print("=== Example 4: Stock Comparison ===")
    response = client.query("Compare Apple, Microsoft, and Google stocks")
    print(f"Response: {response['response']}")
    print(f"Tools Used: {response['tools_used']}")
    print()
    
    # Example 5: Streaming response
    print("=== Example 5: Streaming Response ===")
    print("Question: Give me a market summary")
    print("Streaming response:")
    
    for event in client.stream("Give me a summary of the major market indices"):
        if event['event'] == 'message':
            # Print update
            content = event['data'].get('content', {})
            print(f"  Update: {content}")
        elif event['event'] == 'done':
            print("  Stream completed!")
        elif event['event'] == 'error':
            print(f"  Error: {event['data']}")
    
    print()
    print("=== All Examples Complete ===")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the chatbot API.")
        print("Make sure the server is running on http://localhost:8080")
    except Exception as e:
        print(f"Error: {e}")

