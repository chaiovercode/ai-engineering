from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage, SystemMessage 
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph.message import add_messages
from dotenv import load_dotenv


load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def add(a: int, b: int) -> int:
    """Add 2 numbers"""
    return a + b

tools = [add]

model = ChatOpenAI(
    model='gpt-4o-mini',
    temperature = 0.7
).bind_tools(tools)

def
