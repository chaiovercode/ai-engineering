# AI Agents Foundations

So you want to build an AI agent. Cool.

You've probably watched a dozen YouTube tutorials where someone wraps an OpenAI API call in Python and calls it a day. Sure, that works. But is it production ready? Not even close.

This repo is different. It's everything you need to actually understand AI agents — not just copy-paste and hope. All 8 core patterns. Working code. Production examples. No fluff.

---

## What's In This Folder

```
1_foundations/
├── README.md                  # 👈 This file - How to use everything
├── NEWSLETTER.md              # Standalone article (copy to Medium/blog)
├── complete_tutorial.py       # All 7 patterns with working demos
├── agents/                    # 3 production-ready agents
│   ├── career_agent.py       # Personal AI assistant (RAG + Tools)
│   ├── support_agent.py      # Customer support (Evaluation + Retry)
│   └── research_agent.py     # Multi-agent researcher (Orchestration)
├── me/                        # Your personal data for RAG
│   ├── linkedin.pdf          # Add your LinkedIn PDF here
│   └── summary.txt           # Add your personal summary here
└── requirements.txt           # Dependencies
```

---

## Quick Start

**Step 1: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Set up your API key**
```bash
# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

**Step 3: Run the tutorial**
```bash
python complete_tutorial.py
```

This runs 7 demos showing every pattern in action. Watch it execute. Read the output. Then study the code.

**Step 4: Run a production agent**
```bash
python agents/career_agent.py
```

Open http://127.0.0.1:7860 to see it live.

**Step 5: Make it yours**
```bash
# Edit your info
vim me/summary.txt
# Add your LinkedIn PDF
cp ~/Downloads/your-linkedin.pdf me/linkedin.pdf

# Run it again
python agents/career_agent.py
```

---

## What Even Is An Agent?

"Agent" is one of those words everyone throws around but nobody agrees on.

Anthropic makes a useful distinction:

**Workflows** = You write the code that decides what happens. The LLM does its thing, but you're calling the shots. Step one, step two, step three. Predictable.

**Agents** = The LLM itself decides what to do next. It picks the tools. It figures out the order. You give it a goal and it works out the path.

One follows your playbook. The other writes its own.

---

# The 8 Core Patterns

These patterns power 70% of production AI agents in the wild. Master these, and you can build anything.

## Pattern 1: Basic LLM Calls — The Amnesiac Genius

**Key insight:** LLMs are stateless. Every API call starts fresh. Zero memory.

If you ask "Tell me about France" then "What's the capital?" — the AI has no clue you're still talking about France. It literally doesn't know.

**See it in action:**
- `complete_tutorial.py` → `demo_basic_llm()`

**Code:**
```python
from openai import OpenAI

openai = OpenAI()
messages = [{"role": "user", "content": "What is 2+2?"}]
response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
print(response.choices[0].message.content)
```

**The fix:** Either cram all context into every request, or build something smarter (Pattern 2).

---

## Pattern 2: Conversation Chaining — The Conversation Scribe

**Key insight:** Keep a running transcript. Send it all back each time. Now the AI "remembers."

Think of it like a court stenographer for your AI. Nothing gets lost.

**See it in action:**
- `complete_tutorial.py` → `demo_conversation_chaining()`

**Code:**
```python
messages = []  # Conversation history

while True:
    user_input = input("You: ")
    messages.append({"role": "user", "content": user_input})

    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    ai_response = response.choices[0].message.content

    messages.append({"role": "assistant", "content": ai_response})
    print(f"AI: {ai_response}")
```

**When you need this:** Any multi-step task. Planning, writing, research. Without conversation history, none of that works.

---

## Pattern 3: LLM Orchestration — The Creative Team

**Key insight:** One model to generate, multiple to work, one to judge = better results, lower cost.

A single model trying to generate AND evaluate settles for "good enough." But when you separate the jobs — creative generation versus critical evaluation — you get better outputs.

**See it in action:**
- `complete_tutorial.py` → `demo_llm_orchestration()`
- `agents/research_agent.py` → Full 4-agent research system

**Architecture:**
```
Generator LLM → Creates challenge
    ↓
Worker LLMs → Compete to solve it
    ↓
Judge LLM → Ranks results objectively
```

**The win:** Use cheap models for workers, expensive for judging. GPT-4 quality at GPT-3.5 cost.

---

## Pattern 4: RAG — The Open-Book Exam

**Key insight:** Don't fine-tune. Just stuff context into the prompt.

When a customer asks "How do I reset my device?", grab the relevant section from your manual, put it in the prompt, let the AI answer from that.

**See it in action:**
- `complete_tutorial.py` → `demo_rag_pattern()`
- `agents/career_agent.py` → Loads LinkedIn PDF + summary
- `agents/support_agent.py` → Loads product docs

**Code:**
```python
# Load your documents
with open("me/summary.txt") as f:
    summary = f.read()

# Stuff it into the system prompt
system_prompt = f"""You are a helpful assistant.

Context:
{summary}

Answer based ONLY on the information above."""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What's the main topic?"}
]
```

**Why it won:** Way cheaper and faster than fine-tuning. Answers stay grounded. No hallucinations. This is why ChatGPT added file uploads.

---

## Pattern 5: Tool Use — The Digital Handyman ⭐ MOST IMPORTANT

**Key insight:** This is THE pattern that makes agents actually useful.

By default, an LLM can only talk. Give it access to a weather API? Now it actually checks. Give it database access? Now it can look up real data.

**Tool use transforms the AI from a conversationalist into something that DOES things.**

**See it in action:**
- `complete_tutorial.py` → `demo_tool_use()`
- `agents/career_agent.py` → Uses `record_user_email` tool
- `agents/support_agent.py` → Uses 3 tools (tickets, search, escalation)

**The Flow:**
```
User: "What's the weather in Tokyo?"
    ↓
LLM thinks: "I need to call get_weather(city='Tokyo')"
    ↓
You execute: get_weather() → "72°F and sunny"
    ↓
Add result to messages
    ↓
LLM responds: "It's 72°F and sunny in Tokyo!"
```

**Code:**
```python
# 1. Define the function
def get_weather(city):
    return f"Weather in {city}: 72°F and sunny"

# 2. Describe it to the AI
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }
}]

# 3. Tool execution loop (THE FOUNDATION OF ALL AGENTS)
messages = [{"role": "user", "content": "What's weather in Tokyo?"}]

done = False
while not done:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    if response.choices[0].finish_reason == "tool_calls":
        # Execute tool, add result back, loop
        tool_call = response.choices[0].message.tool_calls[0]
        result = get_weather(city="Tokyo")

        messages.append(response.choices[0].message)
        messages.append({
            "role": "tool",
            "content": json.dumps({"result": result}),
            "tool_call_id": tool_call.id
        })
    else:
        done = True
```

**This loop powers EVERYTHING.** ChatGPT plugins, AI agents, all of it.

---

## Pattern 6: Evaluation — The Quality Control Inspector

**Key insight:** Never trust AI output blindly. Have another AI check it first.

Before your AI's response reaches the user, an Evaluator checks it. Accurate? Any hallucinations? If something's off, regenerate with feedback.

**See it in action:**
- `complete_tutorial.py` → `demo_evaluation()`
- `agents/support_agent.py` → Full evaluation + retry loop

**Code:**
```python
# 1. Agent responds
agent_response = get_agent_response(question)

# 2. Evaluator checks it
evaluation_prompt = f"""
Context: {original_context}
Question: {question}
Response: {agent_response}

Is this accurate? Did the AI hallucinate?
Respond with JSON: {{"is_acceptable": true/false, "feedback": "..."}}
"""

evaluation = evaluator_llm.create(evaluation_prompt)

# 3. If bad, regenerate
if not evaluation['is_acceptable']:
    new_response = agent_llm.create(f"Feedback: {evaluation['feedback']}. Try again.")
```

**Without evaluation, you're hoping your AI doesn't mess up. With evaluation, you're guaranteeing quality.**

Hope is not a strategy in production.

---

## Pattern 7: Production Agent Class — The Professional Blueprint

**Key insight:** Combine all patterns into clean, deployable architecture.

RAG for knowledge. Tools for actions. Conversation history for context. Evaluation for quality. All in one maintainable class.

**See it in action:**
- `complete_tutorial.py` → `ProductionAgent` class
- `agents/career_agent.py` → Full implementation
- `agents/support_agent.py` → With evaluation
- `agents/research_agent.py` → With orchestration

**Architecture:**
```python
class ProductionAgent:
    def __init__(self):
        self.context = self._load_context()  # RAG
        self.tools = self._define_tools()    # Tools
        self.openai = OpenAI()

    def _load_context(self):
        # Load PDFs, docs, etc.
        return documents

    def _system_prompt(self):
        return f"You are X. Context: {self.context}"

    def chat(self, message, history):
        messages = [
            {"role": "system", "content": self._system_prompt()},
            *history,
            {"role": "user", "content": message}
        ]

        # Tool execution loop
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                messages=messages,
                tools=self.tools
            )

            if response.choices[0].finish_reason == "tool_calls":
                execute_tool()  # Pattern 5
            else:
                done = True

        return final_response
```

**This is what separates prototypes from products.**

---

## Pattern 8: Autonomous Agents — The Self-Directed Worker

**Key insight:** AI that makes its own decisions. Powerful but dangerous.

An autonomous agent has a goal, access to tools, and the freedom to figure out how to achieve that goal on its own. It tries approaches, learns from failures, adjusts strategy.

**Example:**
```
Goal: "Debug this failing test suite"
    ↓
Agent reads test file → runs tests → sees 3 failures
    ↓
Agent examines errors → modifies code → runs again
    ↓
2 failures left → continues until all pass
```

**The risk:** An unchecked autonomous agent could:
- Get stuck in loops
- Make irreversible decisions
- Rack up API costs
- Cause actual damage

**When to use:**

✅ **Good use cases:**
- Code generation (can't break production)
- Research tasks (can verify results)
- Data analysis (humans review)
- Content creation (humans approve)

❌ **Bad use cases:**
- Financial transactions (irreversible)
- Medical decisions (life-critical)
- Legal filings (binding)
- Production deployments (high-impact)

**Safety requirements:**
1. Clear success/failure metrics
2. Maximum iteration limits
3. Human oversight gates
4. Rollback capability
5. Cost limits
6. Emergency stop

**Only use when:** The AI can't break anything important, you have clear metrics, humans can intervene, and you've tested in a sandbox.

**Note:** Pattern 8 is intentionally NOT in `complete_tutorial.py`. It's advanced territory with real risks. Master patterns 1-7 first.

---

# The 3 Production Agents

Let's see these patterns in real, deployable code.

## 1. Career Agent (`agents/career_agent.py`)

**What it does:** Personal AI assistant that represents you professionally on your website.

**Patterns used:**
- ✅ RAG (your LinkedIn/resume)
- ✅ Tools (email capture, notifications)
- ✅ Production architecture

**Run it:**
```bash
python agents/career_agent.py
```

**Customize:**
1. Update `me/summary.txt` with your info
2. Add your LinkedIn PDF to `me/linkedin.pdf`
3. Change `name="Your Name"` in the code
4. (Optional) Set `PUSHOVER_USER` and `PUSHOVER_TOKEN` for notifications

**Deploy:**
```bash
uv run gradio deploy
```

Opens at http://127.0.0.1:7860 locally. Deploy command gives you a public URL.

---

## 2. Support Agent (`agents/support_agent.py`)

**What it does:** Customer support bot with automatic quality control.

**Patterns used:**
- ✅ RAG (product docs)
- ✅ Tools (tickets, search, escalation)
- ✅ **Evaluation** (second LLM checks quality)
- ✅ **Retry loop** (auto-regenerates bad responses)

**The flow:**
```
User question
    ↓
Agent responds
    ↓
Evaluator checks → If bad → Regenerate with feedback
    ↓
If good → Return to user
```

**Run it:**
```bash
python agents/support_agent.py
```

**Customize:**
1. Update `PRODUCT_DOCS` and `FAQS` with your product info
2. Change `company_name="Your Company"`
3. Connect real ticketing system (replace simulated functions)

---

## 3. Research Agent (`agents/research_agent.py`)

**What it does:** Multi-agent research system demonstrating orchestration.

**Patterns used:**
- ✅ **Orchestration** (4 specialized agents working together)
- ✅ LLM-as-Judge
- ✅ Conversation chaining

**The agents:**
```
Planner → Breaks topic into questions
    ↓
Researchers → Answer each question (can run in parallel)
    ↓
Analyst → Synthesizes findings into comprehensive report
    ↓
Judge → Evaluates research quality
```

**Run it:**
```bash
python agents/research_agent.py
```

**Try asking:** "What are AI agents and how do they work?"

**Customize:**
1. Replace `simulated_web_search()` with real search API (Tavily, SerpAPI)
2. Add more knowledge sources (databases, APIs)
3. Add citation tracking

---

# What Makes Agents Actually Work

## Feedback is Everything

The best agents get **clear, immediate feedback.** Code compiles or it doesn't. Tests pass or fail. APIs return success or error.

Vague feedback = confused agent wandering aimlessly.

## Humans Stay in the Loop

Even "autonomous" agents need escape hatches. **Always include:**
- Maximum iteration limits
- Triggers that ask for help
- Easy human override
- Approval gates for high-stakes actions

## The Framework Question

LangChain, LangGraph, AutoGen, CrewAI — they're tools, not magic.

**Many successful agents are just 50 lines of Python calling OpenAI directly.** Start simple. Add frameworks if they genuinely help. But understand what's actually happening underneath.

Don't cargo-cult complexity.

---

# The Bottom Line

Building effective AI agents isn't about the fanciest architecture. It's about:

1. **Understanding your actual problem**
2. **Starting with the simplest solution that could work**
3. **Adding complexity only when you've proven you need it**
4. **Making sure you can measure success objectively**

Most "agents" are just chatbots with APIs. And honestly? **That solves most problems just fine.**

Start there. Get it working. Then maybe, maybe consider something fancier.

**The goal isn't to build the most complex agent possible. It's to solve your actual problem in the most reliable way.**

---

# Learning Path

## Week 1: Understand the Patterns
```bash
# Day 1-2: Run and study the tutorial
python complete_tutorial.py

# Day 3-4: Read the code
code complete_tutorial.py    # Read every line
code agents/career_agent.py  # See production structure

# Day 5-6: Experiment
# Modify code, break things, understand why
```

## Week 2: Build Your Agent
```bash
# Customize career agent with YOUR data
vim me/summary.txt
cp ~/Downloads/linkedin.pdf me/linkedin.pdf

python agents/career_agent.py

# Test locally at http://127.0.0.1:7860
```

## Week 3: Ship It
```bash
# Deploy publicly
cd agents
uv run gradio deploy

# Share on LinkedIn
# Add to portfolio
# Get user feedback
# Iterate
```

---

# Quick Reference

## Basic LLM Call
```python
from openai import OpenAI

openai = OpenAI()
messages = [{"role": "user", "content": "Your question"}]
response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
print(response.choices[0].message.content)
```

## Add a Tool
```python
# 1. Define function
def my_tool(param):
    return {"result": "success"}

# 2. Describe it
tools = [{
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {"param": {"type": "string"}},
            "required": ["param"]
        }
    }
}]

# 3. Execute in loop
if tool_name == "my_tool":
    result = my_tool(**arguments)
```

## Load Documents (RAG)
```python
from pypdf import PdfReader

# PDF
reader = PdfReader("file.pdf")
text = "".join([page.extract_text() for page in reader.pages])

# Text
with open("file.txt") as f:
    text = f.read()

# Use in system prompt
system_prompt = f"Context: {text}\n\nAnswer based on this."
```

## Deploy with Gradio
```python
import gradio as gr

agent = ProductionAgent()

interface = gr.ChatInterface(
    fn=agent.chat,
    type="messages",
    title="My AI Agent"
)

interface.launch()  # Local: http://127.0.0.1:7860
```

---

# Mastery Checklist

## Theory
- [ ] Explain why LLMs are stateless
- [ ] Describe the tool execution loop in detail
- [ ] Explain RAG vs fine-tuning
- [ ] Understand orchestration patterns
- [ ] Know why evaluation is critical
- [ ] Understand when NOT to use autonomous agents

## Practice
- [ ] Build RAG agent from scratch (no copy-paste)
- [ ] Implement custom tools for your use case
- [ ] Add evaluation to prevent hallucinations
- [ ] Chain multiple LLM calls into workflow
- [ ] Deploy working agent to production

## Production
- [ ] Handle errors gracefully
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Secure API keys and sensitive data
- [ ] Optimize for cost (token usage, model selection)
- [ ] Add safety checks for autonomous behavior

---

# Files Overview

| File | Purpose | When to use |
|------|---------|-------------|
| `complete_tutorial.py` | Working demos of all 7 patterns | Learning and experimentation |
| `agents/career_agent.py` | Personal AI assistant | Deploy on your website |
| `agents/support_agent.py` | Customer support with evaluation | Customer service use case |
| `agents/research_agent.py` | Multi-agent orchestration | Research and analysis tasks |
| `NEWSLETTER.md` | Standalone article | Share on blog/Medium |
| `me/summary.txt` | Your personal summary | Customize career agent |
| `me/linkedin.pdf` | Your LinkedIn export | Customize career agent |

---

# Production Best Practices

## Security
```python
# ❌ DON'T
api_key = "sk-proj-..."

# ✅ DO
api_key = os.getenv("OPENAI_API_KEY")
```

## Error Handling
```python
# ❌ DON'T
response = openai.chat.completions.create(...)

# ✅ DO
try:
    response = openai.chat.completions.create(...)
except Exception as e:
    logger.error(f"LLM call failed: {e}")
    return "I'm experiencing technical difficulties."
```

## Token Management
```python
# ❌ DON'T
messages = [{"role": "system", "content": entire_database}]  # $$$!

# ✅ DO
recent_messages = history[-10:]  # Last 10 only
context = document[:2000]  # First 2000 chars
```

## Evaluation
```python
# ❌ DON'T
return agent.respond(question)

# ✅ DO
response = agent.respond(question)
if evaluator.check(response):
    return response
else:
    return regenerate_with_feedback()
```

---

# Final Words

**These patterns power 70% of production AI agents in the wild.**

You don't need fancy frameworks to build powerful AI. You need:

1. ✅ Understanding of core patterns
2. ✅ Clean code architecture
3. ✅ Production mindset (evaluation, error handling)
4. ✅ Willingness to ship

**You now have all four.**

The difference between beginners and professionals isn't knowledge — it's execution.

**The tutorials are done. The patterns are learned. The code is ready.**

**Now ship something.** 🚀

---

**Questions? Check `complete_tutorial.py` - every pattern is demonstrated with working code and detailed comments.**

**Want to share? Check `NEWSLETTER.md` - copy-paste ready article version.**
