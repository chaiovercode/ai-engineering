from typing import TypedDict, List
from langgraph.graph import StateGraph
import math

class AgentState(TypedDict):
    name: str
    values: List[int]
    operator: str
    result: str

def process_values(state: AgentState) -> AgentState:
    name = state["name"]
    values = state["values"]
    operator = state["operator"]
    
    if operator == "*":
        total = math.prod(values)
    else:
        total = sum(values)

    state["result"] = f"Hi {name}! Your result is {total}"
    return state

graph = StateGraph(AgentState)

graph.add_node("process", process_values)
graph.set_entry_point("process")
graph.set_finish_point("process")

app = graph.compile()

from IPython.display import Image, display
#save the graph to a file
with open("graph2.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())

result = app.invoke({"name": "Bob", "values": [1, 2, 3, 4], "operator": "+"})
print(result["result"])
