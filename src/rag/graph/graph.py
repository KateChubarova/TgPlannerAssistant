from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from rag.graph.nodes import chatbot
from rag.graph.state import State
from rag.graph.tools import tools

tool_node = ToolNode(tools)

builder = StateGraph(State)

builder.add_node("agent", chatbot)
builder.add_node("tools", tool_node)

builder.set_entry_point("agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()
