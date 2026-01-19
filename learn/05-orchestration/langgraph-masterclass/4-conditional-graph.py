from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    number2: int
    number3: int
    number4: int
    operation: str
    finalNumber: int
    finalNumber2: int

def adder1(state: AgentState) -> AgentState:
    state["finalNumber"] = state["number1"] + state["number2"]
    return state

def subtract1(state: AgentState) -> AgentState:
    state["finalNumber"] = state["number1"] - state["number2"]
    return state

def decide_next_node1(state: AgentState) -> str:
    return "add_node1" if state["operation"] == "+" else "subtract_node1"

def adder2(state: AgentState) -> AgentState:
    state["finalNumber2"] = state["number3"] + state["number4"]
    return state

def subtract2(state: AgentState) -> AgentState:
    state["finalNumber2"] = state["number3"] - state["number4"]
    return state

def decide_next_node2(state: AgentState) -> str:
    return "add_node2" if state["operation"] == "+" else "subtract_node2"

graph = StateGraph(AgentState)

# Nodes
graph.add_node("router1", lambda state: state) #passthrough function
graph.add_node("add_node1", adder1)
graph.add_node("subtract_node1", subtract1)
graph.add_node("router2", lambda state: state) #passthrough function
graph.add_node("add_node2", adder2)
graph.add_node("subtract_node2", subtract2)

# Edges
graph.add_edge(START, "router1")

graph.add_conditional_edges(
    "router1",
    decide_next_node1,
    {
        "add_node1": "add_node1",
        "subtract_node1": "subtract_node1"
    }
)

graph.add_edge("add_node1", "router2")
graph.add_edge("subtract_node1", "router2")

graph.add_conditional_edges(
    "router2",
    decide_next_node2,
    {
        "add_node2": "add_node2",
        "subtract_node2": "subtract_node2"
    }
)

graph.add_edge("add_node2", END)
graph.add_edge("subtract_node2", END)

app = graph.compile()

from IPython.display import Image, display
#save the graph to a file
with open("graph4.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())


result = app.invoke({
    "number1": 10,
    "number2": 20,
    "number3": 30,
    "number4": 40,
    "operation": "+"
})

print(result["finalNumber"] + result["finalNumber2"])