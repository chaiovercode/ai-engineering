from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict, List
from dotenv import load_dotenv
import os

load_dotenv()

class AgentState(TypedDict):
    messages: List[HumanMessage]

llm = ChatOpenAI(
    model = 'gpt-4o-mini',
    temperature = 0.7,
    max_tokens = 3000,
    openai_api_key = os.getenv('OPENAI_API_KEY')
)

def process(state: AgentState) -> AgentState:
    response = llm.stream(state['messages'])
    for chunk in response:
        print(chunk.content, end='', flush=True)
    state['messages'].append(response)
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
app = graph.compile()

user_input = input("User: ")
while user_input != "exit":
    result = app.invoke({
        "messages": [HumanMessage(content=user_input)]
    })
    user_input = input("User: ")

print(f"\nAI: {result['messages']}")


