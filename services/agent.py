from typing import Annotated , Sequence
from typing_extensions import TypedDict
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage , SystemMessage 
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph , END , START 
from langgraph.graph.message import add_messages 
from langgraph.prebuilt import ToolNode 

from services.tools import portfolio_tools

import os 


load_dotenv()

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage],add_messages]


SYSTEM_PROMPT="""You are the official AI Assistant for Moamen's personal portfolio website.
Your role is to assist recruiters, developers, and visitors by providing accurate, professional, and concise answers about Moamen's background, projects, and skills.

Tool Guidelines:
1. When asked about specific skills, frameworks, or tech stack lists (e.g., 'Show me PyTorch projects'), use `filter_projects_by_skill`.
2. For detailed technical inquiries, architecture explanations, or background questions, use `search_portfolio_kb`.
3. If a question is a simple greeting or general talk, respond directly without invoking tools.
4. Always present project links and details cleanly using Markdown formatted bullet points.
"""

llm=ChatGroq(model_name="qwen/qwen3.8-27b",temperature=0,api_key=os.getenv("GROQ_API_KEY"))
llm_with_tools=llm.bind_tools(portfolio_tools)


def call_model(state:AgentState):
    messages=state["messages"]
    if not isinstance(messages[0],SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)]+list(messages)
        llm_response=llm_with_tools.invoke(messages)
    return {"messages":[llm_response]}

def should_continue(state:AgentState):
    last_msg=state["messages"][-1]
    if hasattr(last_msg,"tool_calls") and last_msg.tool_calls:
        return "tools"
    return END

workflow=StateGraph(AgentState)
workflow.add_node("agent",call_model)
workflow.add_node("tools",ToolNode(portfolio_tools)) 

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
                                "agent",
                               should_continue,{
                                   "tools":"tools",
                                    END:END,}
                                    )

workflow.add_edge("tools","agent")

portfolio_agent=workflow.compile()




###Test Block###


if __name__ == "__main__":
    print("--- Testing Portfolio Agent ---\n")
    
    test_query = "What projects did Moamen build using PyTorch?"
    inputs = {"messages": [("user", test_query)]}
    
    # Run the graph and stream the state transitions
    for chunk in portfolio_agent.stream(inputs, stream_mode="values"):
        latest_message = chunk["messages"][-1]
        print(f"[{latest_message.type.upper()}]:")
        print(latest_message.content)
        if hasattr(latest_message, "tool_calls") and latest_message.tool_calls:
            print(f"Tool Calls Triggered: {latest_message.tool_calls}")
        print("-" * 50)

