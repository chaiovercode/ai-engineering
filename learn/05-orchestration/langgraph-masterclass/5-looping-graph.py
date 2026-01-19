from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
import random


class AgentState(TypedDict):
    name: str
    number: List[int]
    counter: int

def greeting(state: AgentState)-> AgentState:
    state["name"] = f"Hey {state['name']}, you are awesome!"
    state["counter"] = 0
    return state

def random_node(state: AgentState)-> AgentState:
    state["number"].append(random.randint(0, 10))
    state["counter"] += 1
    return state

def should_continue(state: AgentState)-> AgentState:
    if state["counter"] < 5:
        return "loop"
    else:
        return END

graph = StateGraph(AgentState)

graph.add_node("greeting", greeting)
graph.add_node("random", random_node)
graph.add_edge(START, "greeting")
graph.add_edge("greeting", "random")

graph.add_conditional_edges(
    "random",
    should_continue,
    {
        "loop": "random",
        END: END
    }
)

app = graph.compile()

from IPython.display import Image, display
#save the graph to a file
with open("graph5.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())

result = app.invoke({
    "name": "Vivek",
    "number": [],
    "counter": 0
})

print(result)
