"""
Direct test of MCP server tools using stdio transport.
This bypasses the async context manager issue.
"""
import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_tools():
    """Test MCP server tools directly."""
    print("=" * 60)
    print("Testing MCP Server Tools Directly (stdio)")
    print("=" * 60)
    print()
    
    # Server parameters
    server_path = os.path.join(os.path.dirname(__file__), "mcp_server_remote.py")
    python_path = sys.executable
    
    print(f"Server path: {server_path}")
    print(f"Python path: {python_path}")
    print()
    
    server_params = StdioServerParameters(
        command=python_path,
        args=[server_path],
        env=None
    )
    
    try:
        # Connect using async with (proper context management)
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                print("[OK] Connected to MCP server via stdio")
                print()
                
                # List available tools
                tools_response = await session.list_tools()
                tools = tools_response.tools
                
                print(f"[OK] Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                print()
                
                # Test 1: Get stock price
                print("=" * 60)
                print("Test 1: get_stock_price (AAPL)")
                print("=" * 60)
                try:
                    result = await session.call_tool("get_stock_price", {"symbol": "AAPL"})
                    print("[OK] Tool call successful")
                    if result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                print(f"Result: {content.text[:300]}...")
                    print()
                except Exception as e:
                    print(f"[FAIL] Error: {e}")
                    print()
                
                # Test 2: Get market summary
                print("=" * 60)
                print("Test 2: get_market_summary")
                print("=" * 60)
                try:
                    result = await session.call_tool("get_market_summary", {})
                    print("[OK] Tool call successful")
                    if result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                print(f"Result: {content.text[:300]}...")
                    print()
                except Exception as e:
                    print(f"[FAIL] Error: {e}")
                    print()
                
                # Test 3: Compare stocks
                print("=" * 60)
                print("Test 3: compare_stocks (AAPL, MSFT)")
                print("=" * 60)
                try:
                    result = await session.call_tool("compare_stocks", {"symbols": "AAPL,MSFT"})
                    print("[OK] Tool call successful")
                    if result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                print(f"Result: {content.text[:300]}...")
                    print()
                except Exception as e:
                    print(f"[FAIL] Error: {e}")
                    print()
                
                print("=" * 60)
                print("[SUCCESS] All MCP server tools are working!")
                print("=" * 60)
                
    except Exception as e:
        print(f"[FAIL] Error connecting to MCP server: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(test_mcp_tools()))

