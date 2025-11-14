"""MCP Client wrapper for connecting to the tool server."""
import os
import sys
import logging
import asyncio
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)


class MCPClientWrapper:
    """Wrapper for MCP client to connect to tool server."""
    
    def __init__(self, transport_protocol: str = "http"):
        """
        Initialize MCP client wrapper.
        
        Args:
            transport_protocol: "stdio" for local process or "http" for remote server
        """
        self.transport_protocol = transport_protocol
        self.session: Optional[ClientSession] = None
        self.tools_cache: list = []
        self._context = None
        self._exit_stack = []
        self._stdio_context = None
        self._http_context = None
        self._session_context = None
        self._is_connected = False
        
        logger.info(f"Initializing MCP client with transport: {transport_protocol}")
    
    async def connect(self):
        """Connect to MCP server and initialize session."""
        if self._is_connected:
            logger.warning("MCP client already connected")
            return
            
        try:
            if self.transport_protocol == "stdio":
                # Local stdio connection
                server_path = os.getenv("MCP_SERVER_PATH", "../mcp_server_remote.py")
                python_path = os.getenv("PYTHON_PATH", sys.executable)
                
                logger.info(f"Connecting to MCP server via stdio: {server_path}")
                
                server_params = StdioServerParameters(
                    command=python_path,
                    args=[server_path],
                    env=None
                )
                
                # Create stdio client context
                self._stdio_context = stdio_client(server_params)
                self._context = await self._stdio_context.__aenter__()
                read, write = self._context
                
                # Create session
                self._session_context = ClientSession(read, write)
                self.session = await self._session_context.__aenter__()
                
            elif self.transport_protocol == "http":
                # Remote HTTP connection
                server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
                
                logger.info(f"Connecting to MCP server via HTTP: {server_url}")
                
                # Create HTTP client context - streamablehttp_client yields (read, write, session_info)
                self._http_context = streamablehttp_client(server_url)
                context_result = await self._http_context.__aenter__()
                
                # HTTP client returns a 3-tuple: (read, write, session_info)
                if len(context_result) == 3:
                    read, write, _session_info = context_result
                else:
                    read, write = context_result
                    
                self._context = context_result
                
                # Create session
                self._session_context = ClientSession(read, write)
                self.session = await self._session_context.__aenter__()
                
            else:
                raise ValueError(f"Unknown transport protocol: {self.transport_protocol}")
            
            # Initialize session
            await self.session.initialize()
            logger.info("MCP session initialized")
            
            # List and cache available tools
            tools_response = await self.session.list_tools()
            self.tools_cache = tools_response.tools
            
            logger.info(f"Found {len(self.tools_cache)} tools: {[tool.name for tool in self.tools_cache]}")
            
            self._is_connected = True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            await self.disconnect()
            raise
    
    async def __aenter__(self):
        """Context manager entry - connect to server."""
        await self.connect()
        return self
    
    async def disconnect(self):
        """Disconnect from MCP server and cleanup resources."""
        if not self._is_connected and self.session is None:
            return
            
        try:
            # Close session first
            if self._session_context is not None:
                try:
                    await self._session_context.__aexit__(None, None, None)
                    logger.debug("Closed session context")
                except Exception as e:
                    logger.error(f"Error closing session context: {str(e)}")
                finally:
                    self._session_context = None
                    self.session = None
            
            # Close transport context
            if self._stdio_context is not None:
                try:
                    await self._stdio_context.__aexit__(None, None, None)
                    logger.debug("Closed stdio context")
                except Exception as e:
                    logger.error(f"Error closing stdio context: {str(e)}")
                finally:
                    self._stdio_context = None
                    
            if self._http_context is not None:
                try:
                    await self._http_context.__aexit__(None, None, None)
                    logger.debug("Closed HTTP context")
                except Exception as e:
                    logger.error(f"Error closing HTTP context: {str(e)}")
                finally:
                    self._http_context = None
            
            self._context = None
            self._is_connected = False
            logger.info("MCP client connection closed")
            
        except Exception as e:
            logger.error(f"Error during MCP client cleanup: {str(e)}")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - disconnect from server."""
        await self.disconnect()
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if not self.session:
            raise RuntimeError("MCP session not initialized. Use 'async with' context manager.")
        
        try:
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            result = await self.session.call_tool(tool_name, arguments)
            
            logger.info(f"Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            raise
    
    def get_tools_for_llm(self) -> list[dict]:
        """
        Convert MCP tools to OpenAI/Groq function calling format.
        
        Returns:
            List of tool definitions in OpenAI format
        """
        tools = []
        
        for tool in self.tools_cache:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or f"Execute {tool.name} tool",
                    "parameters": tool.inputSchema if tool.inputSchema else {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            tools.append(tool_def)
        
        logger.debug(f"Converted {len(tools)} tools to LLM format")
        return tools
    
    def get_tool_names(self) -> list[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools_cache]

