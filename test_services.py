"""
Simple test script to verify MCP server and chatbot backend are working.
"""
import requests
import json
import time
import sys

def test_mcp_server():
    """Test MCP server health."""
    print("=" * 60)
    print("Testing MCP Server (port 8000)")
    print("=" * 60)
    
    try:
        # MCP servers use streamable-http which requires specific headers
        # Let's just check if the port is open
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("[OK] MCP Server is running on port 8000")
            return True
        else:
            print("[FAIL] MCP Server is not responding on port 8000")
            return False
    except Exception as e:
        print(f"[ERROR] Error checking MCP server: {e}")
        return False

def test_chatbot_backend():
    """Test chatbot backend health."""
    print("\n" + "=" * 60)
    print("Testing Chatbot Backend (port 8080)")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Chatbot Backend is healthy")
            print(f"  Status: {data.get('status')}")
            print(f"  Agent Ready: {data.get('agent_ready')}")
            return True
        else:
            print(f"[FAIL] Chatbot Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Chatbot Backend is not running or not responding")
        print("  Make sure the backend is started with: python chatbot-backend/main.py")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking chatbot backend: {e}")
        return False

def test_query():
    """Test a simple query."""
    print("\n" + "=" * 60)
    print("Testing Query Endpoint")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:8080/query",
            json={"message": "What is the current price of Apple stock?"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Query successful!")
            print(f"  Response: {data.get('response', '')[:200]}...")
            print(f"  Tools Used: {data.get('tools_used', [])}")
            print(f"  Session ID: {data.get('session_id', '')}")
            return True
        else:
            print(f"[FAIL] Query failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error testing query: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Market Intelligence Chatbot - Service Tests")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test MCP server
    results.append(("MCP Server", test_mcp_server()))
    
    # Wait a bit
    time.sleep(2)
    
    # Test chatbot backend
    results.append(("Chatbot Backend", test_chatbot_backend()))
    
    # If backend is up, test query
    if results[-1][1]:
        time.sleep(1)
        results.append(("Query Endpoint", test_query()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

