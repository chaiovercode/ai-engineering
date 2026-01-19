from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def process(state: AgentState):
    """This node will process the messages and return the response"""
    response = llm.invoke(state['messages'])
    print(f"\nAI: {response.content}")
    return {"messages": [response]}

# Initialize memory checkpointer
# memory = MemorySaver()
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

# Compile with checkpointer for persistent memory
agent = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "conversation-1"}}

while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        break
    
    # Invoke with config to persist state in memory
    agent.invoke(
        {"messages": [HumanMessage(content=user_input)]}, 
        config=config
    )

# Log the conversation from the persisted state
final_state = agent.get_state(config)
with open("logging.txt", "w") as f:
    for message in final_state.values["messages"]:
        role = "User" if isinstance(message, HumanMessage) else "AI"
        f.write(f"{role}: {message.content}\n")
