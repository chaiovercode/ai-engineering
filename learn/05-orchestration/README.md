# AI Orchestration with LangGraph

> Making multiple AI agents work together.

## What is Orchestration?

**Orchestration** = coordinating multiple AI agents like a conductor leads an orchestra.

Instead of one AI doing everything, you have specialists:

```
One AI doing everything:
┌─────────────────────────────────────────┐
│  AI: Research + Write + Edit + Publish  │  ← Overwhelming!
└─────────────────────────────────────────┘

Multiple specialized AIs:
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Researcher  │──►│   Writer     │──►│   Editor     │
│  (finds info)│   │(writes draft)│   │(polishes it) │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## Why Use Multiple Agents?

| Single Agent | Multiple Agents |
|--------------|-----------------|
| Gets confused with complex tasks | Each agent has one clear job |
| Hard to debug what went wrong | Easy to find which step failed |
| Can't run things in parallel | Agents can work simultaneously |
| One prompt does everything | Specialized prompts per task |

---

## What is LangGraph?

**LangGraph** is a tool for building multi-agent workflows.

Think of it like drawing a flowchart that AI follows:

```
       START
          │
          ▼
    ┌───────────┐
    │ Researcher│
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │   Writer  │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌───────┐ ┌───────────┐
│Editor │ │Fact-Checker│  ← These run IN PARALLEL!
└───┬───┘ └─────┬─────┘
    │           │
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │   Merge   │
    └─────┬─────┘
          │
          ▼
         END
```

---

## The 3 Core Concepts

### 1. State (The Shared Notepad)

All agents share information through **state** - like passing notes.

```python
# Define what information gets passed around
class ArticleState:
    topic: str           # What to write about
    research: str        # Research findings
    draft: str           # Written draft
    edited: str          # Final version
```

Each agent:
- Reads what it needs from state
- Writes its output back to state

---

### 2. Nodes (The Workers)

Each **node** is an agent that does one job.

```python
def researcher(state):
    # Read the topic from state
    topic = state["topic"]

    # Do research (call LLM, search web, etc.)
    findings = search_web(topic)

    # Write results back to state
    return {"research": findings}
```

---

### 3. Edges (The Connections)

**Edges** define the flow - who passes to whom.

```python
# Sequential: one after another
graph.add_edge("researcher", "writer")

# Parallel: both at same time
graph.add_edge("writer", "editor")
graph.add_edge("writer", "fact_checker")

# Merge: wait for both to finish
graph.add_edge("editor", "merge")
graph.add_edge("fact_checker", "merge")
```

---

## Simple Example: Article Pipeline

```
Topic: "AI in Healthcare"
         │
         ▼
┌─────────────────┐
│   RESEARCHER    │  "Found 5 key applications..."
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     WRITER      │  "AI is transforming healthcare..."
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     EDITOR      │  "AI is revolutionizing healthcare..."
└────────┬────────┘
         │
         ▼
    Final Article
```

---

## Parallel Execution (The Power Move)

The killer feature: **run agents at the same time**.

```
Without parallel (Sequential):
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Step 1   │──►│ Step 2   │──►│ Step 3   │
│ (10 sec) │   │ (10 sec) │   │ (10 sec) │
└──────────┘   └──────────┘   └──────────┘
Total time: 30 seconds

With parallel:
              ┌──────────┐
         ┌───►│ Step 2a  │───┐
         │    │ (10 sec) │   │
┌──────────┐  └──────────┘   │  ┌──────────┐
│ Step 1   │──               ├─►│ Step 3   │
│ (10 sec) │──               │  │ (10 sec) │
└──────────┘  ┌──────────┐   │  └──────────┘
         └───►│ Step 2b  │───┘
              │ (10 sec) │
              └──────────┘
Total time: 20 seconds (saved 10 seconds!)
```

---

## When to Use Orchestration

**Use it when:**
- Task has multiple distinct steps
- Steps can run in parallel
- You need to debug which step failed
- Different steps need different models/prompts

**Don't use it when:**
- Simple question-answer
- Single-step tasks
- Adding complexity isn't worth it

---

## Real-World Example: Research Assistant

```
User: "Write a blog post about quantum computing"

┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                           │
│  │  STRATEGIST  │ ← Plans what to research                  │
│  │  (Web search)│                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │    WRITER    │ ← Writes the draft                        │
│  │              │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│    ┌────┴────┐                                              │
│    │         │                                               │
│    ▼         ▼                                               │
│ ┌──────┐ ┌──────────┐                                       │
│ │EDITOR│ │FACT-CHECK│ ← Run at the SAME TIME                │
│ └──┬───┘ └────┬─────┘                                       │
│    │          │                                              │
│    └────┬─────┘                                              │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │    MERGE     │ ← Combines both results                   │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Output: Polished, fact-checked blog post
```

---

## Conditional Routing

Sometimes you want different paths based on conditions:

```
       User Question
            │
            ▼
     ┌──────────────┐
     │  CLASSIFIER  │  "Is this technical or general?"
     └──────┬───────┘
            │
     ┌──────┴──────┐
     │             │
     ▼             ▼
┌─────────┐  ┌─────────┐
│TECHNICAL│  │ SIMPLE  │
│ EXPERT  │  │RESPONDER│
└─────────┘  └─────────┘

"How does TCP work?" → Technical Expert
"What's your name?" → Simple Responder
```

---

## Building a Graph (Step by Step)

```python
from langgraph.graph import StateGraph, START, END

# 1. Define your state (shared data)
class MyState:
    input: str
    output: str

# 2. Create the graph
graph = StateGraph(MyState)

# 3. Add nodes (workers)
graph.add_node("researcher", researcher_function)
graph.add_node("writer", writer_function)

# 4. Connect them (edges)
graph.add_edge(START, "researcher")
graph.add_edge("researcher", "writer")
graph.add_edge("writer", END)

# 5. Compile and run
app = graph.compile()
result = app.invoke({"input": "AI trends"})
```

---

## Streaming Progress

See what's happening as agents work:

```python
for event in graph.stream(initial_state):
    for node_name, output in event.items():
        print(f"✓ {node_name} completed")

# Output:
# ✓ researcher completed
# ✓ writer completed
# ✓ editor completed
# ✓ fact_checker completed
# ✓ merge completed
```

Great for showing progress to users!

---

## Key Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Sequential | A → B → C | Step-by-step tasks |
| Parallel | A → (B & C) → D | Independent subtasks |
| Conditional | A → if X then B else C | Different paths based on input |
| Loop | A → B → (back to A?) | Revision cycles |

---

## Try It Yourself

```bash
cd 05-orchestration
pip install -r requirements.txt
python langgraph_basics.py
```

This demonstrates:
- Sequential graphs
- Parallel execution
- Conditional routing

---

## Key Takeaways

1. **Orchestration = Multiple agents working together**
2. **State = Shared notepad** between agents
3. **Nodes = Workers** that do one job
4. **Edges = Connections** defining the flow
5. **Parallel execution** saves time when steps are independent

---

## Next Steps

→ [06-observability](../06-observability/) - Monitor what your agents are doing
