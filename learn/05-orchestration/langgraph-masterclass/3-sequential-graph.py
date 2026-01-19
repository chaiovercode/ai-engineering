from typing import TypedDict, List
from langgraph.graph import StateGraph
import math

class AgentState(TypedDict):
    name: str
    age: str
    skills: List[str]
    final: str

def first_node(state: AgentState) -> AgentState:
    """Process the name and start the final message."""
    state["final"] = f"Hi {state['name']}"
    return state

def second_node(state: AgentState) -> AgentState:
    """Process the age and append it to the final message."""
    state["final"] = f"{state['final']}. You are {state['age']} years old"
    return state

def third_node(state: AgentState) -> AgentState:
    """Process the skills and append it to the final message."""
    skills_str = ", ".join(state["skills"])
    state["final"] = f"{state['final']}. You have these skills {skills_str}."
    return state

graph = StateGraph(AgentState)

graph.add_node("first", first_node)
graph.add_node("second", second_node)
graph.add_node("third", third_node)

graph.set_entry_point("first")
graph.add_edge("first", "second")
graph.add_edge("second", "third")
graph.set_finish_point("third")

app = graph.compile()

from IPython.display import Image, display
#save the graph to a file
with open("graph3.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())

result = app.invoke({"name": "vivek", "age": "35", "skills": ["python", "java", "c++"]})
print(result["final"])




