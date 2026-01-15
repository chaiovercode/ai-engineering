# AI Observability

> See what your AI is actually doing.

## What is Observability?

**Observability** = The ability to understand what's happening inside your AI system by looking at its outputs.

Think of it like a car dashboard:
- Speed (latency)
- Fuel level (cost)
- Engine warning lights (errors)
- Trip computer (metrics)

Without observability, your AI is a **black box**:

```
User Question ──►  [??? MYSTERY ???]  ──► Answer

With observability:

User Question ──► [Step 1] ──► [Step 2] ──► [Step 3] ──► Answer
                    │            │            │
                    ▼            ▼            ▼
                 Logged       Logged       Logged
                 2.3 sec      1.1 sec      0.8 sec
                 500 tokens   200 tokens   150 tokens
```

---

## Why Does This Matter?

### The Problem

AI systems are unpredictable. Same question, different responses. Sometimes wrong answers.

**Common issues:**
- "Why did the AI say that?"
- "Why is this so slow?"
- "How much is this costing me?"
- "Which part is broken?"

### The Solution

Track everything. Know exactly what happened.

---

## LangSmith: The AI Dashboard

**LangSmith** is an observability platform for AI apps (made by the LangChain team).

```
┌─────────────────────────────────────────────────────────┐
│                    LANGSMITH DASHBOARD                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Metrics                                              │
│  ├── Total requests: 1,234                              │
│  ├── Avg latency: 2.3s                                  │
│  ├── Error rate: 0.5%                                   │
│  └── Total cost: $12.34                                 │
│                                                          │
│  🔍 Recent Traces                                        │
│  ├── "What is AI?" - 1.2s - Success                     │
│  ├── "Explain quantum" - 3.4s - Success                 │
│  └── "Write code..." - ERROR - Token limit              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### 1. Traces (The Full Journey)

A **trace** is the complete record of one request.

```
Trace: "Write a blog post about AI"

├── START (user submits request)
│
├── Step 1: Researcher
│   ├── Input: "AI trends"
│   ├── Output: "Found 5 key points..."
│   ├── Time: 3.2 seconds
│   └── Tokens: 450
│
├── Step 2: Writer
│   ├── Input: "5 key points..."
│   ├── Output: "AI is transforming..."
│   ├── Time: 5.1 seconds
│   └── Tokens: 1,200
│
├── Step 3: Editor
│   ├── Input: "AI is transforming..."
│   ├── Output: "Final polished article..."
│   ├── Time: 2.3 seconds
│   └── Tokens: 800
│
└── END (total: 10.6 seconds, 2,450 tokens)
```

---

### 2. Runs (Individual Steps)

Each step in a trace is a **run**.

```
Trace (one user request)
├── Run: Researcher (one AI call)
├── Run: Writer (one AI call)
└── Run: Editor (one AI call)
```

---

### 3. Metrics (The Numbers)

What LangSmith tracks automatically:

| Metric | What It Means | Why It Matters |
|--------|---------------|----------------|
| **Latency** | How long it took | User experience |
| **Tokens** | Input + output tokens | Cost |
| **Cost** | $ spent on API calls | Budget |
| **Errors** | Failed requests | Reliability |
| **Feedback** | Quality scores | Improvement |

---

## Latency Percentiles Explained

You'll see P50, P95, P99 - here's what they mean:

```
P50 (Median): Half of requests are faster than this
P95: 95% of requests are faster than this
P99: 99% of requests are faster than this
```

**Example:**
```
P50 = 2 seconds  ← Typical experience
P95 = 5 seconds  ← Occasional slow request
P99 = 15 seconds ← Rare worst case (1 in 100)
```

**Why P99 matters:** That 1 in 100 user having a bad experience will complain!

---

## Setting Up LangSmith

It's just environment variables:

```bash
# In your .env file
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-key-here
LANGCHAIN_PROJECT=my-ai-app
```

That's it! All LangChain/LangGraph calls are now traced automatically.

---

## Debugging with LangSmith

### Scenario: Slow Response

```
User complains: "Your AI took forever!"

Step 1: Open LangSmith
Step 2: Find the trace
Step 3: See the breakdown:

        ┌──────────────────────────────────────┐
        │ Trace: 45 seconds total              │
        ├──────────────────────────────────────┤
        │ Researcher: 3 sec ✓                  │
        │ Writer: 5 sec ✓                      │
        │ Fact-Checker: 35 sec ← PROBLEM!      │
        │   └── Web search: 30 sec ← ROOT CAUSE│
        │ Editor: 2 sec ✓                      │
        └──────────────────────────────────────┘

Fix: Add timeout to web search
```

---

### Scenario: Wrong Answer

```
User complains: "The AI made something up!"

Step 1: Find the trace
Step 2: Look at the inputs/outputs:

        ┌──────────────────────────────────────┐
        │ Writer Input:                        │
        │ "Write about Python 3.12"            │
        │                                      │
        │ Fact-Checker Output:                 │
        │ "Claims verified: 2/5" ← PROBLEM!    │
        │ - Made up feature names              │
        │ - Wrong release date                 │
        └──────────────────────────────────────┘

Fix: Improve fact-checker prompt
```

---

## RAG Evaluation Metrics

For RAG (document-based AI), track these quality scores:

### Faithfulness

**Is the answer based on the documents, or did AI make it up?**

```
Context: "Python was created in 1991"

Good answer: "Python was created in 1991"
Faithfulness: 100% ✓

Bad answer: "Python was created in 1991 and is the most popular language"
Faithfulness: 50% ✗ (second claim not in context)
```

---

### Answer Relevance

**Did the AI actually answer the question?**

```
Question: "How do I install Python?"

Good answer: "Download from python.org and run the installer"
Relevance: High ✓

Bad answer: "Python is a programming language created by..."
Relevance: Low ✗ (didn't answer the question)
```

---

### Context Precision

**Did we retrieve the RIGHT documents?**

```
Question: "What's the return policy?"

Retrieved:
1. Return Policy document ✓ Relevant
2. Shipping FAQ ✗ Not relevant
3. About Us page ✗ Not relevant

Precision: 1/3 = 33% (too much junk!)
```

---

### Context Recall

**Did we find ALL the needed documents?**

```
Question: "What are all the payment methods?"

Needed documents: [Credit Card, PayPal, Bank Transfer]
Retrieved: [Credit Card, PayPal]

Recall: 2/3 = 67% (missed Bank Transfer doc!)
```

---

## Quick Reference

### What to Monitor

| Metric | Alert If | Action |
|--------|----------|--------|
| P99 Latency | > 30 seconds | Optimize slow steps |
| Error Rate | > 5% | Check logs, fix bugs |
| Faithfulness | < 80% | Improve RAG/prompts |
| Daily Cost | > $100 | Review token usage |

---

### Debugging Workflow

```
1. FIND the problem trace
   └── Filter by: errors, high latency, low scores

2. EXPAND the trace
   └── See each step's inputs and outputs

3. IDENTIFY the issue
   └── Which step failed? Why?

4. FIX and verify
   └── Make changes, check new traces
```

---

## Try It Yourself

```bash
cd 06-observability
pip install -r requirements.txt

# Set up LangSmith (free tier available)
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-key

# Run examples
python 01_langsmith_basics.py
python 04_rag_evaluation.py

# Check smith.langchain.com to see your traces!
```

---

## Key Takeaways

1. **Observability = See inside your AI** (not a black box)
2. **Traces show the full journey** of each request
3. **Latency, tokens, cost** - track the numbers
4. **P50/P95/P99** - understand different user experiences
5. **RAG metrics** - faithfulness, relevance, precision, recall
6. **LangSmith** - automatic tracing with environment variables

---

## You've Completed the Learning Path! 🎉

You now understand:
- ✅ How LLMs work (fundamentals)
- ✅ How to write effective prompts
- ✅ How to use LLM APIs
- ✅ How to build AI agents
- ✅ How to orchestrate multiple agents
- ✅ How to monitor and debug AI systems

**Next:** Check out the `apps/` folder for real-world examples!
