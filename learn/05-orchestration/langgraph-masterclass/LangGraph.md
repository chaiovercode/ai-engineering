# LangGraph Quick Reference

## Common Imports
```python
# Graph
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Prebuilt
from langgraph.prebuilt import ToolNode, create_react_agent

# Checkpointing
from langgraph.checkpoint.memory import InMemorySaver

# Messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

# Tools
from langchain_core.tools import tool

# Typing
from typing import Annotated, TypedDict
```

---

## 1. Core Concepts

**State** - "The shared data that flows through your graph"
```python
class State(TypedDict):
    messages: list
    context: str
```

**Node** - "A function that does work and updates state"
```python
def process_node(state: State) -> dict:
    return {"messages": state["messages"] + ["done"]}
```

**Edge** - "A connection from one node to another"
```python
graph.add_edge("node_a", "node_b")
```

**START / END** - "Entry and exit points"
```python
from langgraph.graph import START, END
```

---

## 2. Message Types

```python
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    RemoveMessage,
    BaseMessage
)
```

**HumanMessage** - "What the user says"
```python
HumanMessage(content="Hello, how are you?")
```

**AIMessage** - "What the LLM responds"
```python
AIMessage(content="I'm doing great!")
```

**SystemMessage** - "Instructions for the LLM"
```python
SystemMessage(content="You are a helpful assistant.")
```

**ToolMessage** - "Result from a tool call"
```python
ToolMessage(content="72°F sunny", tool_call_id="call_123")
```

**RemoveMessage** - "Delete a message from history"
```python
RemoveMessage(id="msg_to_remove")
```

**Shorthand Tuples**
```python
messages = [
    ("system", "You are helpful."),
    ("human", "Hi!"),
    ("ai", "Hello!")
]
```

---

## 3. Runnables

**Runnable** - "Anything you can invoke, stream, or batch"
```python
from langchain_core.runnables import RunnableLambda

# LLMs, chains, tools, graphs are all Runnables
result = runnable.invoke(input)
results = runnable.batch([input1, input2])
for chunk in runnable.stream(input):
    print(chunk)
```

**RunnableLambda** - "Turn any function into a Runnable"
```python
def add_one(x: int) -> int:
    return x + 1

runnable = RunnableLambda(add_one)
runnable.invoke(5)  # Returns 6
```

**Chain with Pipe** - "Connect Runnables together"
```python
chain = prompt | llm | output_parser
result = chain.invoke({"topic": "cats"})
```

**RunnablePassthrough** - "Pass input unchanged"
```python
from langchain_core.runnables import RunnablePassthrough

chain = {
    "context": retriever,
    "question": RunnablePassthrough()
} | prompt | llm
```

---

## 4. Building a Graph

```python
from langgraph.graph import StateGraph, START, END

# 1. Define state
class State(TypedDict):
    messages: list

# 2. Create graph
graph = StateGraph(State)

# 3. Add nodes
graph.add_node("fetch", fetch_data)
graph.add_node("process", process_data)

# 4. Connect nodes
graph.add_edge(START, "fetch")
graph.add_edge("fetch", "process")
graph.add_edge("process", END)

# 5. Compile & run
app = graph.compile()
result = app.invoke({"messages": []})
```

---

## 5. Control Flow

**Conditional Edge** - "Choose next node based on state"
```python
def router(state: State) -> str:
    if state["needs_review"]:
        return "review"
    return "output"

graph.add_conditional_edges("check", router)
```

**Loops** - "Keep running until done"
```python
def should_continue(state: State) -> str:
    if state["iterations"] < 3:
        return "process"  # Loop back
    return END

graph.add_conditional_edges("process", should_continue)
```

**Branching** - "Route to different handlers"
```python
def route_by_type(state: State) -> str:
    match state["type"]:
        case "text": return "text_handler"
        case "image": return "image_handler"
        case _: return "default"
```

---

## 6. State Management

**Annotated State** - "Control how updates merge"
```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]  # Appends & manages by ID
    count: int                                # Replaces old value
```

**Custom Reducer**
```python
def keep_last_5(old: list, new: list) -> list:
    return (old + new)[-5:]

class State(TypedDict):
    history: Annotated[list, keep_last_5]
```

---

## 7. Tools

**Define Tool** - "A function the LLM can call"
```python
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"
```

**Bind to LLM**
```python
llm_with_tools = llm.bind_tools([search, calculator])
```

**ToolNode** - "Executes tool calls automatically"
```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode([search, calculator])
graph.add_node("tools", tool_node)
```

**How ToolNode Works**
1. Receives AIMessage with tool_calls
2. Executes each tool
3. Returns ToolMessage for each result
```python
# Input: AIMessage with tool_calls
# Output: [ToolMessage(content="result", tool_call_id="..."), ...]
```

---

## 8. Agents

**Prebuilt ReAct Agent** - "Ready to use agent"
```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, tools=[search])
result = agent.invoke({"messages": [("user", "Hello")]})
```

**Custom Agent Loop**
```python
def agent(state: State) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: State) -> str:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

graph.add_node("agent", agent)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")  # Loop back
```

**Multi-Agent**
```python
graph.add_node("researcher", researcher_agent)
graph.add_node("writer", writer_agent)
graph.add_edge("researcher", "writer")
```

---

## 9. Subgraphs

**Subgraph** - "A graph inside a graph"
```python
# Create inner graph
inner = StateGraph(State)
inner.add_node("step1", step1_fn)
inner.add_node("step2", step2_fn)
inner.add_edge(START, "step1")
inner.add_edge("step1", "step2")
inner.add_edge("step2", END)
inner_compiled = inner.compile()

# Use in outer graph
outer = StateGraph(State)
outer.add_node("pre", pre_process)
outer.add_node("inner", inner_compiled)  # Add as node
outer.add_node("post", post_process)
outer.add_edge(START, "pre")
outer.add_edge("pre", "inner")
outer.add_edge("inner", "post")
outer.add_edge("post", END)
```

**Why Subgraphs?**
- Break complex flows into manageable pieces
- Reuse common patterns across graphs
- Encapsulate agent logic

---

## 10. Streaming

**Stream Events** - "Get updates as they happen"
```python
for event in app.stream({"messages": []}, stream_mode="values"):
    print(event)
```

**Stream Modes**
```python
# "values" - Full state after each node
for state in app.stream(input, stream_mode="values"):
    print(state["messages"][-1])

# "updates" - Only the changes from each node
for update in app.stream(input, stream_mode="updates"):
    print(update)

# "messages" - Stream LLM tokens as they generate
for msg, metadata in app.stream(input, stream_mode="messages"):
    print(msg.content, end="")
```

**Async Streaming**
```python
async for event in app.astream(input, stream_mode="values"):
    print(event)
```

---

## 11. Persistence

**Checkpointing** - "Save and resume state"
```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
app = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke(state, config)
```

**Human in the Loop** - "Pause for approval"
```python
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["dangerous_action"]
)

# First run - stops at interrupt
result = app.invoke(input, config)

# User approves... then resume
result = app.invoke(None, config)
```

---

## Quick Patterns

**Simple Pipeline**
```
START → fetch → process → output → END
```

**Agent Loop**
```
START → agent ⟷ tools → END
```

**Branching**
```
START → router → [handler_a, handler_b, handler_c] → END
```

**Multi-Agent**
```
START → researcher → writer → reviewer → END
```
