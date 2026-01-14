"""
LangGraph Research Pipeline

A multi-agent research pipeline with parallel execution for fact-checking and editing.
Replaces the sequential CrewAI implementation with true parallelization.
"""

import os
from typing import TypedDict, Literal
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from ddgs import DDGS

# Initialize LLM (gpt-4o-mini is faster AND cheaper than gpt-3.5-turbo)
llm = ChatOpenAI(model="gpt-4o-mini")

# Search cache for faster repeated queries
_search_cache = {}


def duckduckgo_search(query: str) -> str:
    """Search DuckDuckGo for current, recent information."""
    if query in _search_cache:
        return _search_cache[query]

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if results:
                output = f"Recent search results for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    output += f"{i}. {result.get('title', 'Untitled')}\n"
                    output += f"   {result.get('body', '')[:300]}\n"
                    output += f"   Source: {result.get('href', '')}\n\n"
                _search_cache[query] = output
                return output
            result = f"No recent results found for '{query}'"
            _search_cache[query] = result
            return result
    except Exception as e:
        return f"Could not search for '{query}': {str(e)}"


# State schema
class ResearchState(TypedDict):
    input: str                    # User's topic/query
    mode: Literal['gen-z', 'analytical']
    research: str                 # Output from strategist
    draft: str                    # Output from writer
    fact_checked: str             # Output from fact checker
    edited: str                   # Output from editor
    final: str                    # Merged + processed output


# Prompt builders
def get_strategist_prompt(topic: str, mode: str) -> str:
    if mode == 'gen-z':
        return f"""Research the topic: "{topic}"

Your task is to:
1. Focus on what's CURRENT in 2026 - we are now in January 2026
2. Find recent articles, news, and updates from 2025-2026
3. Identify what's trending RIGHT NOW in 2026, not old stuff from 2023
4. Look for good sources (but keep it real)
5. Put together a vibe check outline with what matters TODAY

IMPORTANT: Avoid outdated information from 2023 or earlier. Focus on recent 2025-2026 developments.
Find recent, actually useful info that slaps. No cap.

Use the search tool to find current information."""
    else:
        return f"""Conduct comprehensive research on: "{topic}"

Your task is to:
1. Focus exclusively on CURRENT 2026 information - we are in January 2026
2. Identify recent trends, partnerships, announcements, and developments from 2025-2026
3. Avoid outdated information from 2023 - focus on RECENT 2025-2026 trends instead
4. Locate latest expert commentary and recent market analysis from 2025-2026
5. Develop a structured, evidence-based research outline grounded in CURRENT 2026 data

CRITICAL: It is now 2026. Do NOT cite 2023 information. Focus ONLY on recent 2025-2026 developments.
Use the search tool to find current market intelligence and recent company announcements."""


def get_writer_prompt(mode: str) -> str:
    if mode == 'gen-z':
        return """Using the research provided, write something that actually hits.

IMPORTANT - Use proper markdown formatting:
- Start with # for the main title
- Use ## for major sections
- Use ### for subsections

Keep it:
1. Real and relatable from the jump
2. Organized with clear headings (# ## ###)
3. Packed with actual facts and insights
4. Chill but smart (you know the vibe)
5. Stuff people can actually use

Make it something people actually want to read."""
    else:
        return """Using the research provided, write an analytical piece on this topic.

IMPORTANT - Use proper markdown formatting:
- Start with # for the main title
- Use ## for major sections
- Use ### for subsections

Requirements:
1. Establish context and significance in the introduction
2. Organize with clear markdown headings (# ## ###)
3. Integrate evidence, data, and quotes with proper attribution
4. Maintain rigorous, professional tone throughout
5. Conclude with synthesis and implications

The piece should be comprehensive and well-structured with proper headings."""


def get_fact_checker_prompt(mode: str) -> str:
    base = """CRITICAL: You MUST verify every factual claim in the content.

For EVERY factual claim (stats, records, dates, quotes):
1. Search for the claim to verify it
2. Compare what the content says vs what you find
3. If wrong, REPLACE with the correct info
4. If you can't verify it, REMOVE the claim

DO NOT just pass through content. Actually verify each claim.

Return the corrected content with all facts verified."""
    return base


def get_editor_prompt(mode: str) -> str:
    if mode == 'gen-z':
        return """Polish this piece without losing the vibe.

Check:
1. Does it actually flow?
2. Is the voice consistent?
3. Grammar and spelling tight?
4. Sentences hit the way they should?
5. Formatting looks clean?
6. Headlines work for search?
7. H1/H2/H3 headings exist?

Keep it real while making it shine. Light touch only.
Return the polished content."""
    else:
        return """Review and refine this analytical piece for excellence.

Focus on:
1. Logical flow and argument coherence
2. Consistency in analysis and perspective
3. Correctness of grammar, syntax, and terminology
4. Academic rigor and citation accuracy
5. Professional formatting and structure
6. Search-friendly headline
7. Proper H1/H2/H3 heading structure

Elevate the analysis while preserving intellectual rigor. Light touch.
Return the refined content."""


# Node functions
def strategist_node(state: ResearchState) -> dict:
    """Content Strategist: Research the topic using web search."""
    topic = state["input"]
    mode = state["mode"]

    # First, do searches to gather information
    search_results = []
    search_queries = [
        f"{topic} 2026",
        f"{topic} latest news",
        f"{topic} trends 2025 2026",
    ]

    for query in search_queries:
        result = duckduckgo_search(query)
        search_results.append(result)

    combined_search = "\n\n".join(search_results)

    prompt = get_strategist_prompt(topic, mode)
    messages = [
        SystemMessage(content="You are an expert content strategist. Use the search results provided to create a comprehensive research outline."),
        HumanMessage(content=f"{prompt}\n\nSearch Results:\n{combined_search}")
    ]

    response = llm.invoke(messages)
    return {"research": response.content}


def writer_node(state: ResearchState) -> dict:
    """Blog Writer: Write engaging content based on research."""
    mode = state["mode"]
    research = state["research"]

    prompt = get_writer_prompt(mode)
    messages = [
        SystemMessage(content="You are a talented writer who excels at crafting engaging, informative content."),
        HumanMessage(content=f"{prompt}\n\nResearch to use:\n{research}")
    ]

    response = llm.invoke(messages)
    return {"draft": response.content}


def fact_checker_node(state: ResearchState) -> dict:
    """Fact Checker: Verify and correct factual claims using search."""
    mode = state["mode"]
    draft = state["draft"]

    # Extract key claims and verify them
    # First, identify claims that need verification
    extract_messages = [
        SystemMessage(content="Extract 3-5 key factual claims (statistics, dates, figures) from this content that need verification."),
        HumanMessage(content=draft)
    ]
    claims_response = llm.invoke(extract_messages)

    # Search for each claim
    verification_results = duckduckgo_search(f"verify {state['input']} facts statistics")

    prompt = get_fact_checker_prompt(mode)
    messages = [
        SystemMessage(content="You are a meticulous fact checker. Verify claims and correct any errors."),
        HumanMessage(content=f"{prompt}\n\nContent to fact-check:\n{draft}\n\nVerification search results:\n{verification_results}")
    ]

    response = llm.invoke(messages)
    return {"fact_checked": response.content}


def editor_node(state: ResearchState) -> dict:
    """Content Editor: Polish the content for clarity and SEO."""
    mode = state["mode"]
    draft = state["draft"]  # Edit the original draft (runs in parallel with fact checker)

    prompt = get_editor_prompt(mode)
    messages = [
        SystemMessage(content="You are a fast, efficient editor who polishes content quickly."),
        HumanMessage(content=f"{prompt}\n\nContent to edit:\n{draft}")
    ]

    response = llm.invoke(messages)
    return {"edited": response.content}


def merge_node(state: ResearchState) -> dict:
    """Merge fact-checked content with editorial improvements."""
    fact_checked = state.get("fact_checked", "")
    edited = state.get("edited", "")

    # Merge: use fact-checked content as base, incorporate editorial improvements
    messages = [
        SystemMessage(content="Merge these two versions of the content. Use the fact-checked version as the primary source (it has verified facts), but incorporate any stylistic improvements from the edited version."),
        HumanMessage(content=f"Fact-checked version:\n{fact_checked}\n\n---\n\nEdited version:\n{edited}\n\nCreate a final merged version that combines accurate facts with polished writing.")
    ]

    response = llm.invoke(messages)
    return {"final": response.content}


# Build the graph
def build_research_graph():
    """Build the LangGraph research pipeline with parallel execution."""
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("strategist", strategist_node)
    graph.add_node("writer", writer_node)
    graph.add_node("fact_checker", fact_checker_node)
    graph.add_node("editor", editor_node)
    graph.add_node("merge", merge_node)

    # Sequential: START → strategist → writer
    graph.add_edge(START, "strategist")
    graph.add_edge("strategist", "writer")

    # Parallel: writer → [fact_checker, editor]
    graph.add_edge("writer", "fact_checker")
    graph.add_edge("writer", "editor")

    # Merge parallel results
    graph.add_edge("fact_checker", "merge")
    graph.add_edge("editor", "merge")

    # End
    graph.add_edge("merge", END)

    return graph.compile()


# Create compiled graph
research_graph = build_research_graph()


def run_research(input_text: str, mode: str, callback=None) -> str:
    """
    Run the research pipeline with optional progress callbacks.

    Args:
        input_text: The topic to research
        mode: 'gen-z' or 'analytical'
        callback: Optional callback function for progress updates

    Returns:
        The final research content
    """
    initial_state = {
        "input": input_text,
        "mode": mode,
        "research": "",
        "draft": "",
        "fact_checked": "",
        "edited": "",
        "final": "",
    }

    # Map node names to display names
    node_display_names = {
        "strategist": "Content Strategist",
        "writer": "Blog Writer",
        "fact_checker": "Fact Checker",
        "editor": "Content Editor",
        "merge": "Finalizing",
    }

    # Track which nodes have completed
    completed_nodes = set()

    # Run with streaming to get node-by-node updates
    for event in research_graph.stream(initial_state, stream_mode="updates"):
        for node_name, node_output in event.items():
            display_name = node_display_names.get(node_name, node_name)

            if callback and node_name not in completed_nodes:
                callback({
                    "type": "agent_complete",
                    "agent": display_name,
                    "output": "",
                })
                completed_nodes.add(node_name)

    # Get final state
    final_state = research_graph.invoke(initial_state)
    return final_state.get("final", final_state.get("draft", ""))


async def run_research_async(input_text: str, mode: str, callback=None) -> str:
    """
    Async version of run_research with progress callbacks.
    """
    initial_state = {
        "input": input_text,
        "mode": mode,
        "research": "",
        "draft": "",
        "fact_checked": "",
        "edited": "",
        "final": "",
    }

    node_display_names = {
        "strategist": "Content Strategist",
        "writer": "Blog Writer",
        "fact_checker": "Fact Checker",
        "editor": "Content Editor",
        "merge": "Finalizing",
    }

    node_phases = {
        "Content Strategist": [
            "Searching for recent trends...",
            "Analyzing market data...",
            "Compiling research findings...",
        ],
        "Blog Writer": [
            "Creating engaging introduction...",
            "Writing main content...",
            "Crafting conclusion...",
        ],
        "Fact Checker": [
            "Identifying claims...",
            "Verifying statistics...",
            "Correcting inaccuracies...",
        ],
        "Content Editor": [
            "Checking grammar...",
            "Improving flow...",
            "Optimizing headings...",
        ],
        "Finalizing": [
            "Merging results...",
            "Final polish...",
        ],
    }

    active_nodes = set()
    completed_nodes = set()
    final_result = None

    async for event in research_graph.astream(initial_state, stream_mode="updates"):
        for node_name, node_output in event.items():
            display_name = node_display_names.get(node_name, node_name)

            # Send start event
            if display_name not in active_nodes and display_name not in completed_nodes:
                active_nodes.add(display_name)
                if callback:
                    phases = node_phases.get(display_name, ["Processing..."])
                    callback({
                        "type": "agent_start",
                        "agent": display_name,
                        "message": phases[0],
                    })

            # Send progress updates
            if callback and display_name in active_nodes:
                callback({
                    "type": "agent_progress",
                    "agent": display_name,
                    "progress": 100,
                    "message": "",
                })

            # Send complete event
            if display_name not in completed_nodes:
                completed_nodes.add(display_name)
                active_nodes.discard(display_name)
                if callback:
                    callback({
                        "type": "agent_complete",
                        "agent": display_name,
                        "output": "",
                    })

            # Capture final result
            if "final" in node_output and node_output["final"]:
                final_result = node_output["final"]

    return final_result or ""
