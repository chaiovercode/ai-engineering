from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    name: str

def greeting_node(state: AgentState) -> AgentState:
    state["name"] = f"Hey {state['name']}, you are awesome!"
    return state

graph = StateGraph(AgentState)

graph.add_node("greeter", greeting_node)
graph.add_edge(START, "greeter")
graph.add_edge("greeter", END)

app = graph.compile()

from IPython.display import Image, display
#save the graph to a file
with open("graph1.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())

result = app.invoke({"name": "Bob"})
print(result["name"])


