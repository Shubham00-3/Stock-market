"""Agent state definition for LangGraph."""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State schema for the market intelligence agent."""
    
    messages: Annotated[list, add_messages]
    session_id: str

