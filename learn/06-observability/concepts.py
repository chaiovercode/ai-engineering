"""
Observability for AI Applications

Observability = The ability to understand a system's internal state
by examining its external outputs (logs, metrics, traces).

Why it matters for AI:
- LLM outputs are non-deterministic
- Small prompt changes can cause big behavior changes
- You need to debug "why did the AI say that?"
- Cost and latency tracking is critical

This module covers LangSmith - the observability platform for LLM apps.
"""

import os
from dotenv import load_dotenv
from langsmith import Client
from langsmith.run_trees import RunTree

load_dotenv()

# =============================================================================
# CONCEPT 1: What LangSmith Traces
# =============================================================================
"""
LangSmith automatically captures:

1. Input/Output     - Full prompts and responses
2. Intermediate     - Every step in a chain/agent
3. Latency          - Time per operation (ms)
4. Token Usage      - Input/output token counts
5. Cost             - Calculated from tokens + model pricing
6. Errors           - Stack traces when things fail
7. Tags/Metadata    - Custom labels you add
8. Feedback         - Quality scores from evaluation

Setup is just environment variables:
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=your_key
    LANGCHAIN_PROJECT=your_project
"""


# =============================================================================
# CONCEPT 2: Core Terminology
# =============================================================================
"""
Project     - Your LLM application (e.g., "research-assistant")
Trace       - One complete execution (e.g., one user request)
Run         - A single operation within a trace (e.g., one LLM call)
Span        - A nested run within a run

Example hierarchy:
    Trace: research-request-123
    ├── Run: strategist_node (15s)
    │   ├── Span: web_search (2s)
    │   └── Span: llm_call (12s)
    ├── Run: writer_node (20s)
    │   └── Span: llm_call (20s)
    └── Run: fact_checker_node (18s)
        └── Span: llm_call (18s)
"""


# =============================================================================
# CONCEPT 3: Manual Tracing
# =============================================================================

def manual_tracing_example():
    """
    How to manually create traces when not using LangChain.
    Useful for custom pipelines or non-LangChain code.
    """
    client = Client()

    # Create a parent trace
    run = RunTree(
        name="my_custom_pipeline",
        run_type="chain",
        inputs={"query": "What is AI?"},
        project_name="learn-observability"
    )

    # Create child operations
    retrieval_run = run.create_child(
        name="retrieval",
        run_type="retriever",
        inputs={"query": "What is AI?"}
    )
    retrieval_run.end(outputs={"documents": ["doc1", "doc2"]})

    generation_run = run.create_child(
        name="generation",
        run_type="llm",
        inputs={"prompt": "Based on docs, explain AI"}
    )
    generation_run.end(outputs={"response": "AI is..."})

    # End the parent trace
    run.end(outputs={"final_answer": "AI is..."})
    run.post()

    return run.id


# =============================================================================
# CONCEPT 4: Adding Feedback/Scores
# =============================================================================

def add_evaluation_scores(run_id: str, scores: dict):
    """
    Attach quality scores to a trace.
    These appear in the LangSmith dashboard.
    """
    client = Client()

    for metric_name, score in scores.items():
        client.create_feedback(
            run_id=run_id,
            key=metric_name,
            score=score,
            comment=f"Auto-evaluated {metric_name}"
        )


# =============================================================================
# CONCEPT 5: Key Metrics to Track
# =============================================================================
"""
Latency Percentiles:
    P50 (median)  - Typical user experience
    P95           - 95% of requests are faster
    P99           - Worst-case (1 in 100)

Quality Metrics (from evaluation):
    Faithfulness      - Is answer grounded in context? (0-1)
    Answer Relevance  - Does it address the question? (0-1)
    Correctness       - Is the answer right? (0-1)

Cost Metrics:
    Tokens per request
    Cost per request ($)
    Daily/monthly spend

Error Metrics:
    Error rate (%)
    Error types (timeouts, rate limits, etc.)
"""


# =============================================================================
# CONCEPT 6: Debugging Workflow
# =============================================================================
"""
When something goes wrong, use this workflow:

1. FIND THE TRACE
   - Filter by: error, high latency, low score, or user report

2. EXPAND THE TREE
   - See all runs/spans with timing

3. IDENTIFY THE BOTTLENECK
   - Which operation took too long?
   - Which operation produced bad output?

4. ANALYZE INPUTS/OUTPUTS
   - Was the prompt wrong?
   - Was the context missing key info?
   - Did the model hallucinate?

5. FIX AND VERIFY
   - Change prompt/retrieval/model
   - Check new traces show improvement

Example investigation:
    Trace: 145s total (way over P99 of 60s)
    ├── strategist: 15s ✓
    ├── writer: 25s ✓
    ├── fact_checker: 85s ← BOTTLENECK!
    │   ├── extract_claims: 10s
    │   ├── web_search: 65s ← ROOT CAUSE (timeout)
    │   └── verify: 10s
    └── merge: 8s ✓

    Fix: Add timeout + fallback for web search
"""


if __name__ == "__main__":
    print("="*60)
    print("LangSmith Observability Concepts")
    print("="*60)

    print("""
Key Takeaways:
1. Set LANGCHAIN_TRACING_V2=true for automatic tracing
2. Every LLM call, tool use, and chain step is captured
3. Use traces to debug slow or wrong responses
4. Attach feedback scores for quality tracking
5. Monitor P50/P95/P99 latency and error rates

To see your traces:
    1. Go to smith.langchain.com
    2. Select your project
    3. Click on any trace to see the full execution tree
""")
