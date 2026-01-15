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
# CONCEPT 6: Simple Definitions (The Jargon-Free Guide)
# =============================================================================
"""
Think of your RAG system like a student taking an open-book exam.

QUALITY METRICS (How good is the answer?)
-----------------------------------------

Answer Relevance:
    The Question: "Did I actually answer what you asked?"
    Simple Def: If you ask "What is the capital of France?" and I say
    "Paris," relevance is high. If I say "France has nice cheese,"
    relevance is low.

Faithfulness:
    The Question: "Did I stick to the textbook (context)?"
    Simple Def: This measures hallucinations. If the documents say
    "Sky is Green" and your bot answers "Sky is Blue" (because it
    knows that from real life), Faithfulness goes down. It *must*
    rely on the provided text.


RETRIEVAL METRICS (How good is the search?)
-------------------------------------------

Context Precision:
    The Question: "How much junk did I pull up?"
    Simple Def: If you retrieved 10 pages to answer a question, but
    only 2 were useful, your precision is low. High precision means
    very little noise.

Context Recall:
    The Question: "Did I find *everything* needed?"
    Simple Def: If the answer requires 3 specific facts and your
    search only found 2 of them, your recall is bad. You missed
    a piece of the puzzle.

MRR (Mean Reciprocal Rank):
    The Question: "How far did I have to scroll to find the right doc?"
    Simple Def:
        - If the perfect document is #1 on the list = Score is 1.0
        - If it's #2 = Score is 0.5
        - If it's #10 = Score is 0.1
        - You want this number close to 1.0


SPEED METRICS (P50 & P99)
-------------------------
This is about Latency (how long the user waits).

P50 (The Median / The "Average Joe"):
    Definition: 50% of your users got an answer faster than this time.
    Real Talk: This is the "normal" experience. If P50 is 2.69s,
    most people wait about 3 seconds.

P99 (The "Worst Case" / The Slowest 1%):
    Definition: 99% of requests were faster than this; this represents
    the slowest 1% of users.
    Real Talk: This is your "lag spike." If P99 is 42s, it means 1 out
    of every 100 users got stuck waiting 42 seconds. You usually look
    at this to find bugs or massive documents that choke the system.


QUICK SUMMARY CHECKLIST
-----------------------
    Faithfulness = Don't lie / Don't use outside info
    Relevance    = Don't ramble
    Precision    = Don't fetch junk docs
    Recall       = Don't miss key docs
    P99          = How bad is the lag for the unluckiest user?
"""


# =============================================================================
# CONCEPT 7: Debugging Workflow
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


# =============================================================================
# CONCEPT 8: Senior-Level Strategy (Beyond Definitions)
# =============================================================================
"""
Knowing definitions is Junior-level. Knowing WHEN and HOW to use them is Senior.

OFFLINE VS ONLINE EVALUATION
----------------------------
You cannot run expensive RAGAS metrics on every chat in production.
It would cost a fortune and be too slow.

Offline Eval (The Lab):
    When:  Before you deploy (CI/CD pipeline)
    What:  Run RAGAS against a "Golden Dataset" - 50 manually verified
           Q&A pairs that represent ideal behavior
    Goal:  "Did my code change break the bot?"

Online Eval (The Real World):
    When:  Live user traffic
    What:  Track User Feedback (thumbs up/down) and Latency (P99).
           Run RAGAS on a random 1% sample, not 100%.
    Goal:  "Are users happy right now?"


TRACING VS METRICS (The "Why" vs "What")
----------------------------------------
Metrics tell you SOMETHING is wrong. Traces tell you WHY.

    Metric:  "The error rate is 5%"
             → Tells you something is broken

    Trace:   "Show me Request ID #123 step-by-step"
             → Tells you the LLM took 15s because Retriever
               fetched a 5MB document

    Strategy: Use Metrics to get ALERTS.
              Use Tracing to find ROOT CAUSE.


THE COST EQUATION (The Manager's Favorite)
------------------------------------------
For senior roles, you must care about money.

Token Types:
    Input Tokens  = Cheaper  (the prompt you send)
    Output Tokens = Expensive (the response you get)

Cost Monitoring Strategy:
    - Track token usage PER USER to prevent budget drain
    - Monitor "Mean Tokens per Query" to catch prompt bloat
    - If costs spike, check if prompts are getting too long
      or if retrieval is pulling too much context


JUNIOR VS SENIOR ANSWERS
------------------------
┌─────────────────┬──────────────────────────┬─────────────────────────────────────┐
│ Concept         │ Junior (Definition)      │ Senior (Strategy)                   │
├─────────────────┼──────────────────────────┼─────────────────────────────────────┤
│ RAGAS           │ "Measures Faithfulness   │ "I run RAGAS in CI/CD. Every PR     │
│                 │  and Relevance"          │  runs against a Golden Dataset"     │
├─────────────────┼──────────────────────────┼─────────────────────────────────────┤
│ Faithfulness    │ "Did the AI hallucinate?"│ "Critical for compliance. If low,   │
│                 │                          │  check if chunks are too small"     │
├─────────────────┼──────────────────────────┼─────────────────────────────────────┤
│ Context         │ "Signal-to-noise ratio"  │ "If low, my re-ranker isn't working.│
│ Precision       │                          │  Consider switching to Cross-Encoder│
├─────────────────┼──────────────────────────┼─────────────────────────────────────┤
│ P99 Latency     │ "Slowest 1% of requests" │ "If spiking, use Tracing to find    │
│                 │                          │  the slow step (big doc? timeout?)" │
├─────────────────┼──────────────────────────┼─────────────────────────────────────┤
│ User Feedback   │ "Thumbs up or down"      │ "This is Ground Truth. Filter by    │
│                 │                          │  'thumbs down' to build failure set"│
└─────────────────┴──────────────────────────┴─────────────────────────────────────┘


COMMON INTERVIEW GOTCHA
-----------------------
Q: "RAGAS requires an LLM to grade an LLM. Isn't that slow and expensive?"

A: "Exactly. That's why we don't run it on live traffic. We run it OFFLINE
    on a small test set, or sample only 1% of production for QA."

This answer shows you understand the Offline vs Online distinction -
the key to running these tools in a real company.
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
