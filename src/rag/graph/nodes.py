from langchain_openai import ChatOpenAI

from rag.graph.tools import tools

llm = ChatOpenAI(model="gpt-4o-mini")

llm_with_tools = llm.bind_tools(tools)


def chatbot(state):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}
