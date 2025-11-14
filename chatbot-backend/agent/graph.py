"""LangGraph agent for market intelligence using Groq LLM."""
import logging
from typing import Literal, Any
import json

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from mcp_client.client import MCPClientWrapper
from utils.cache import ResponseCache

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a highly intelligent Market Intelligence AI assistant powered by advanced financial data tools. Your role is to help users understand stock markets, analyze companies, track market trends, and make informed decisions.

You have access to the following capabilities:
- Real-time stock prices and detailed company metrics
- Historical price data and trends analysis
- Latest financial news from reputable sources
- Stock comparison across multiple companies
- Major market indices overview (S&P 500, Dow Jones, NASDAQ, Russell 2000)

Guidelines:
1. Always provide accurate, data-driven insights based on the tools available
2. When presenting stock data, highlight key metrics like price changes, volume, and market cap
3. For historical data, identify trends and patterns
4. When comparing stocks, present side-by-side comparisons clearly
5. Include relevant market context when discussing individual stocks
6. Cite your sources when presenting news articles
7. Be concise but thorough in your analysis
8. If data is unavailable or tools fail, explain this clearly to the user
9. Never provide investment advice - only objective analysis
10. Format numbers appropriately (e.g., use M for millions, B for billions)

Always think step by step and use the appropriate tools to gather information before responding."""


class MarketIntelligenceAgent:
    """LangGraph-based agent for market intelligence queries."""
    
    def __init__(self, groq_api_key: str, model: str = "llama3-8b-8192"):
        """
        Initialize the market intelligence agent.
        
        Args:
            groq_api_key: Groq API key
            model: Groq model to use (default: llama3-8b-8192)
        """
        self.groq_api_key = groq_api_key
        self.model = model
        
        # Initialize LLM
        self.llm = ChatGroq(
            model=model,
            temperature=0.7,
            api_key=groq_api_key,
            max_tokens=2048
        )
        
        # Initialize MCP client
        transport = os.getenv("MCP_TRANSPORT_PROTOCOL", "http")
        self.mcp_client = MCPClientWrapper(transport_protocol=transport)
        
        # Initialize cache
        self.cache = ResponseCache(default_ttl=300)  # 5 minute cache
        
        # Graph components
        self.graph = None
        self.memory = MemorySaver()
        
        logger.info(f"Initialized MarketIntelligenceAgent with model: {model}")
    
    async def initialize(self):
        """Initialize the agent by connecting to MCP server and building graph."""
        try:
            # Connect to MCP server
            await self.mcp_client.connect()
            logger.info("MCP client connected successfully")
            
            # Build the LangGraph workflow
            self._build_graph()
            logger.info("Agent graph built successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.mcp_client.disconnect()
            logger.info("Agent cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Create workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self._tools_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edge from agent
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile graph with memory
        self.graph = workflow.compile(checkpointer=self.memory)
        
        logger.info("LangGraph workflow compiled")
    
    async def _agent_node(self, state: AgentState) -> dict:
        """
        Agent reasoning node - decides what to do next.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with new messages
        """
        try:
            messages = state["messages"]
            
            # Get tools in LLM format
            tools = self.mcp_client.get_tools_for_llm()
            
            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(tools)
            
            # Prepare messages with system prompt
            full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            
            # Invoke LLM
            response = await llm_with_tools.ainvoke(full_messages)
            
            logger.info(f"Agent response: {response.content[:100] if response.content else 'Tool calls'}")
            
            return {"messages": [response]}
            
        except Exception as e:
            logger.error(f"Error in agent node: {str(e)}")
            error_message = AIMessage(
                content=f"I encountered an error while processing your request: {str(e)}"
            )
            return {"messages": [error_message]}
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Determine if we should continue to tools or end.
        
        Args:
            state: Current agent state
            
        Returns:
            "continue" if tools need to be called, "end" otherwise
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if there are tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.info(f"Continuing to tools: {[tc['name'] for tc in last_message.tool_calls]}")
            return "continue"
        
        logger.info("Ending agent loop")
        return "end"
    
    async def _tools_node(self, state: AgentState) -> dict:
        """
        Tools execution node - executes requested tools.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with tool results
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_messages = []
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]
            
            try:
                # Check cache first
                cached_result = self.cache.get(tool_name, **tool_args)
                
                if cached_result:
                    logger.info(f"Using cached result for {tool_name}")
                    result = cached_result
                else:
                    # Call the tool via MCP
                    logger.info(f"Executing tool: {tool_name}")
                    mcp_result = await self.mcp_client.call_tool(tool_name, tool_args)
                    
                    # Extract content from MCP result
                    if hasattr(mcp_result, 'content') and mcp_result.content:
                        # Handle list of content items
                        if isinstance(mcp_result.content, list):
                            result = {}
                            for item in mcp_result.content:
                                if hasattr(item, 'text'):
                                    # Try to parse as JSON
                                    try:
                                        result = json.loads(item.text)
                                    except:
                                        result = {"result": item.text}
                        else:
                            result = {"result": str(mcp_result.content)}
                    else:
                        result = {"result": str(mcp_result)}
                    
                    # Cache the result
                    self.cache.set(tool_name, result, ttl=300, **tool_args)
                
                # Create tool message
                tool_message = ToolMessage(
                    content=json.dumps(result, indent=2),
                    tool_call_id=tool_call_id,
                    name=tool_name
                )
                tool_messages.append(tool_message)
                
                logger.info(f"Tool {tool_name} executed successfully")
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                
                # Create error message
                error_result = {
                    "error": str(e),
                    "tool": tool_name
                }
                tool_message = ToolMessage(
                    content=json.dumps(error_result),
                    tool_call_id=tool_call_id,
                    name=tool_name
                )
                tool_messages.append(tool_message)
        
        return {"messages": tool_messages}
    
    async def invoke(self, message: str, session_id: str) -> tuple[str, list[str]]:
        """
        Process a user message and return response.
        
        Args:
            message: User message
            session_id: Session identifier for conversation memory
            
        Returns:
            Tuple of (response_text, tools_used)
        """
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "session_id": session_id
            }
            
            # Run the graph
            config = {"configurable": {"thread_id": session_id}}
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # Extract response
            messages = final_state["messages"]
            last_message = messages[-1]
            
            response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
            
            # Extract tools used
            tools_used = []
            for msg in messages:
                if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
                    tools_used.extend([tc["name"] for tc in msg.tool_calls])
            
            logger.info(f"Invoke completed. Tools used: {tools_used}")
            
            return response_text, tools_used
            
        except Exception as e:
            logger.error(f"Error in invoke: {str(e)}")
            return f"I encountered an error: {str(e)}", []
    
    async def stream(self, message: str, session_id: str):
        """
        Stream agent responses.
        
        Args:
            message: User message
            session_id: Session identifier for conversation memory
            
        Yields:
            Response chunks
        """
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "session_id": session_id
            }
            
            # Stream the graph
            config = {"configurable": {"thread_id": session_id}}
            
            async for event in self.graph.astream(initial_state, config):
                logger.debug(f"Stream event: {event}")
                yield event
                
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
            yield {"error": str(e)}


# Import os at the top
import os

