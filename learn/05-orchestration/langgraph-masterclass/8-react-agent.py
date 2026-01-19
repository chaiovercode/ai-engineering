from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage, SystemMessage 
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

#Annotated - provides additonal context without affecting the type itself. it adds metadata to the type
#Reducer Function - takes the current state and the new input and returns the new state which is the add_messages in this case

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

tools = [add]

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
).bind_tools(tools)

def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="You are a helpful assistant who give roasts the users before giving the answer")
    response = model.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> AgentState:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "continue"
    else:
        return "end"

graph = StateGraph(AgentState)

graph.add_node("our_agent", model_call)

#add a tool node 
tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.add_edge(START, "our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

graph.add_edge("tools", "our_agent")

agent = graph.compile()

#invoke the agent
    
user_input = str(input("User: "))

for event in agent.stream({"messages": [HumanMessage(content=user_input)]}):
    for value in event.values():
        print(value["messages"][-1].content)






