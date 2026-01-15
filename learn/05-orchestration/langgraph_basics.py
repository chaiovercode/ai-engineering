"""
LangGraph Basics - Building Multi-Agent Pipelines

This demonstrates the core patterns:
1. State definition with TypedDict
2. Node functions
3. Sequential and parallel edges
4. Streaming execution
"""

import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# =============================================================================
# PATTERN 1: Simple Sequential Graph
# =============================================================================

class SimpleState(TypedDict):
    topic: str
    research: str
    article: str


def researcher(state: SimpleState) -> dict:
    """Research a topic."""
    topic = state["topic"]
    response = llm.invoke(f"Research key facts about: {topic}")
    return {"research": response.content}


def writer(state: SimpleState) -> dict:
    """Write an article based on research."""
    research = state["research"]
    response = llm.invoke(f"Write a short article using these facts:\n{research}")
    return {"article": response.content}


def build_simple_graph():
    """Build a simple sequential graph: researcher -> writer"""
    graph = StateGraph(SimpleState)

    # Add nodes
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)

    # Add edges (sequential)
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


# =============================================================================
# PATTERN 2: Parallel Execution (Fan-Out/Fan-In)
# =============================================================================

class ParallelState(TypedDict):
    topic: str
    draft: str
    fact_check: str
    style_check: str
    final: str


def draft_writer(state: ParallelState) -> dict:
    """Write initial draft."""
    response = llm.invoke(f"Write a short draft about: {state['topic']}")
    return {"draft": response.content}


def fact_checker(state: ParallelState) -> dict:
    """Check facts in the draft (runs in parallel with style_checker)."""
    response = llm.invoke(
        f"Review this for factual accuracy. List any issues:\n{state['draft']}"
    )
    return {"fact_check": response.content}


def style_checker(state: ParallelState) -> dict:
    """Check style (runs in parallel with fact_checker)."""
    response = llm.invoke(
        f"Review this for writing style. List improvements:\n{state['draft']}"
    )
    return {"style_check": response.content}


def merge_feedback(state: ParallelState) -> dict:
    """Merge feedback from both checkers (waits for both to complete)."""
    response = llm.invoke(f"""
Improve this draft using the feedback:

DRAFT:
{state['draft']}

FACT CHECK FEEDBACK:
{state['fact_check']}

STYLE FEEDBACK:
{state['style_check']}

Write the improved version:
""")
    return {"final": response.content}


def build_parallel_graph():
    """
    Build a graph with parallel execution:

              ┌─── fact_checker ───┐
    writer ───┤                    ├─── merge
              └─── style_checker ──┘
    """
    graph = StateGraph(ParallelState)

    # Add nodes
    graph.add_node("writer", draft_writer)
    graph.add_node("fact_checker", fact_checker)
    graph.add_node("style_checker", style_checker)
    graph.add_node("merge", merge_feedback)

    # Edges
    graph.add_edge(START, "writer")

    # Fan-out: writer triggers BOTH checkers in parallel
    graph.add_edge("writer", "fact_checker")
    graph.add_edge("writer", "style_checker")

    # Fan-in: merge waits for BOTH checkers
    graph.add_edge("fact_checker", "merge")
    graph.add_edge("style_checker", "merge")

    graph.add_edge("merge", END)

    return graph.compile()


# =============================================================================
# PATTERN 3: Conditional Routing
# =============================================================================

class ConditionalState(TypedDict):
    query: str
    category: str
    response: str


def classifier(state: ConditionalState) -> dict:
    """Classify the query type."""
    response = llm.invoke(
        f"Classify this query as 'technical' or 'general': {state['query']}"
    )
    category = "technical" if "technical" in response.content.lower() else "general"
    return {"category": category}


def technical_responder(state: ConditionalState) -> dict:
    """Handle technical queries."""
    response = llm.invoke(
        f"Give a detailed technical answer to: {state['query']}"
    )
    return {"response": response.content}


def general_responder(state: ConditionalState) -> dict:
    """Handle general queries."""
    response = llm.invoke(
        f"Give a friendly, simple answer to: {state['query']}"
    )
    return {"response": response.content}


def route_by_category(state: ConditionalState) -> str:
    """Route to appropriate responder based on category."""
    return "technical" if state["category"] == "technical" else "general"


def build_conditional_graph():
    """
    Build a graph with conditional routing:

                    ┌─── technical_responder ───┐
    classifier ─────┤                           ├─── END
                    └─── general_responder ─────┘
    """
    graph = StateGraph(ConditionalState)

    graph.add_node("classifier", classifier)
    graph.add_node("technical", technical_responder)
    graph.add_node("general", general_responder)

    graph.add_edge(START, "classifier")

    # Conditional edge based on classification
    graph.add_conditional_edges(
        "classifier",
        route_by_category,
        {
            "technical": "technical",
            "general": "general"
        }
    )

    graph.add_edge("technical", END)
    graph.add_edge("general", END)

    return graph.compile()


# =============================================================================
# STREAMING EXECUTION
# =============================================================================

def run_with_streaming(graph, initial_state: dict):
    """Run graph and stream progress updates."""
    print("\n" + "="*60)
    print("Starting execution...")
    print("="*60)

    for event in graph.stream(initial_state, stream_mode="updates"):
        for node_name, output in event.items():
            print(f"\n✓ {node_name} completed")
            # Show first 100 chars of each output
            for key, value in output.items():
                preview = str(value)[:100] + "..." if len(str(value)) > 100 else value
                print(f"  {key}: {preview}")


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("PATTERN 1: Sequential Graph")
    print("="*60)
    simple_graph = build_simple_graph()
    result = simple_graph.invoke({"topic": "quantum computing"})
    print(f"\nFinal article:\n{result['article'][:300]}...")

    print("\n" + "="*60)
    print("PATTERN 2: Parallel Execution")
    print("="*60)
    parallel_graph = build_parallel_graph()
    run_with_streaming(parallel_graph, {"topic": "climate change"})

    print("\n" + "="*60)
    print("PATTERN 3: Conditional Routing")
    print("="*60)
    conditional_graph = build_conditional_graph()

    # Technical query
    result1 = conditional_graph.invoke({"query": "How does TCP/IP work?"})
    print(f"\nTechnical query routed to: {result1['category']}")

    # General query
    result2 = conditional_graph.invoke({"query": "What's a good book to read?"})
    print(f"General query routed to: {result2['category']}")
