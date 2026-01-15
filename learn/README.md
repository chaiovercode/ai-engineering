# Learn AI Engineering

> From zero to building AI applications.

## What is AI Engineering?

**AI Engineering** = Building real applications with AI (not just chatting with ChatGPT).

```
Regular AI User:
┌─────────────────────────────────────────┐
│  Type question → Get answer → Done      │
└─────────────────────────────────────────┘

AI Engineer:
┌─────────────────────────────────────────┐
│  Build apps that use AI automatically   │
│  ├── Customer support bots              │
│  ├── Document analyzers                 │
│  ├── Research assistants                │
│  └── Code generators                    │
└─────────────────────────────────────────┘
```

---

## The Learning Path

Follow these 6 steps in order. Each builds on the previous one.

```
START HERE
    │
    ▼
┌─────────────────┐
│ 1. FUNDAMENTALS │  ← How does AI actually work?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. PROMPTING    │  ← How to ask AI the right way
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. LLM APIs     │  ← Talk to AI with code
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. AGENTS       │  ← AI that can DO things
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. ORCHESTRATION│  ← Multiple AIs working together
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. OBSERVABILITY│  ← See what your AI is doing
└────────┬────────┘
         │
         ▼
    BUILD APPS!
```

---

## Quick Overview

### 📚 [01-fundamentals](./01-fundamentals/)
**What you'll learn:** How LLMs work, what tokens are, why AI "forgets" things.

Think of it like: Understanding how a car engine works before driving.

```bash
cd 01-fundamentals && python concepts.py
```

---

### ✍️ [02-prompt-engineering](./02-prompt-engineering/)
**What you'll learn:** 6 techniques to get better answers from AI.

Think of it like: Learning how to ask good questions.

```bash
cd 02-prompt-engineering && python techniques.py
```

---

### 🔌 [03-llm-apis](./03-llm-apis/)
**What you'll learn:** Call AI from your code (OpenAI, Claude).

Think of it like: Instead of texting a friend, your code texts the AI.

```bash
cd 03-llm-apis && python openai_basics.py
```

---

### 🤖 [04-agents](./04-agents/)
**What you'll learn:** Build AI that can take actions (search, calculate, send emails).

Think of it like: Giving your AI hands and feet, not just a mouth.

```bash
cd 04-agents && python 01_tool_use.py
```

---

### 🎭 [05-orchestration](./05-orchestration/)
**What you'll learn:** Multiple AI agents working as a team.

Think of it like: Instead of one employee, you have a team with specialists.

```bash
cd 05-orchestration && python langgraph_basics.py
```

---

### 📊 [06-observability](./06-observability/)
**What you'll learn:** Monitor what your AI is doing, find and fix problems.

Think of it like: A car dashboard showing speed, fuel, and warning lights.

```bash
cd 06-observability && python 01_langsmith_basics.py
```

---

## The Big Picture

Here's how everything connects:

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR AI APPLICATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User: "Write a blog post about AI"                            │
│                    │                                             │
│                    ▼                                             │
│   ┌──────────────────────────────────────────────────┐          │
│   │              ORCHESTRATION (5)                    │          │
│   │  Researcher → Writer → Editor → Fact-Checker     │          │
│   └──────────────────────────────────────────────────┘          │
│                    │                                             │
│                    ▼                                             │
│   ┌──────────────────────────────────────────────────┐          │
│   │                 AGENTS (4)                        │          │
│   │  Each agent uses tools (search, calculate, etc.) │          │
│   └──────────────────────────────────────────────────┘          │
│                    │                                             │
│                    ▼                                             │
│   ┌──────────────────────────────────────────────────┐          │
│   │                LLM APIs (3)                       │          │
│   │  Send messages to OpenAI/Claude, get responses   │          │
│   └──────────────────────────────────────────────────┘          │
│                    │                                             │
│                    ▼                                             │
│   ┌──────────────────────────────────────────────────┐          │
│   │              PROMPTS (2)                          │          │
│   │  Carefully crafted instructions for each agent   │          │
│   └──────────────────────────────────────────────────┘          │
│                    │                                             │
│                    ▼                                             │
│   ┌──────────────────────────────────────────────────┐          │
│   │             FUNDAMENTALS (1)                      │          │
│   │  Understanding tokens, context, temperature      │          │
│   └──────────────────────────────────────────────────┘          │
│                    │                                             │
│   ┌──────────────────────────────────────────────────┐          │
│   │            OBSERVABILITY (6)                      │          │
│   │  Watching everything, tracking metrics           │          │
│   └──────────────────────────────────────────────────┘          │
│                                                                  │
│   Output: Polished, fact-checked blog post                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Setup (Do This First!)

### Step 1: Get API Keys

You need accounts with AI providers:

| Provider | Sign Up | What You Get |
|----------|---------|--------------|
| OpenAI | [platform.openai.com](https://platform.openai.com) | GPT-4 access |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | Claude access |
| LangSmith | [smith.langchain.com](https://smith.langchain.com) | Free monitoring |

### Step 2: Create Environment File

Create a file called `.env` in this folder:

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
LANGCHAIN_API_KEY=your-langsmith-key-here
LANGCHAIN_TRACING_V2=true
```

### Step 3: Install Python Packages

```bash
# For each section:
pip install -r 01-fundamentals/requirements.txt
pip install -r 02-prompt-engineering/requirements.txt
# ... and so on
```

---

## Key Concepts Summary

| Concept | Simple Explanation | Why It Matters |
|---------|-------------------|----------------|
| **LLM** | A smart autocomplete that predicts the next word | It's the brain behind AI apps |
| **Token** | A chunk of text (roughly 3/4 of a word) | You pay per token |
| **Context Window** | AI's "short-term memory" (what it can see) | Bigger = more expensive |
| **Prompt** | The instructions you give the AI | Better prompts = better results |
| **Agent** | AI that can take actions | Makes AI actually useful |
| **RAG** | AI + Your Documents | AI that knows YOUR stuff |
| **Trace** | Recording of what the AI did | Debug problems faster |

---

## Common Questions

### "How long will this take?"
- Each section: 1-2 hours to understand
- Full path: A weekend of focused learning

### "Do I need to know Python?"
- Basic Python helps, but examples are simple
- Copy-paste friendly code

### "How much will API calls cost?"
- Learning: $1-5 total (using cheap models)
- Most examples use `gpt-4o-mini` which is very affordable

### "What if something doesn't work?"
- Check your API keys are correct
- Make sure you have internet connection
- Read the error message (usually helpful!)

---

## After Learning

Once you complete all 6 sections:

1. **Check `../apps/`** - See real applications built with these concepts
2. **Build something** - Best way to learn is to create
3. **Add observability** - Always know what your AI is doing

---

## Resources

- 📖 [AI Engineering Book](./resources/AI%20Engineering.pdf) - Comprehensive reference
- 🔗 [LangChain Docs](https://python.langchain.com/) - Framework documentation
- 🔗 [OpenAI Docs](https://platform.openai.com/docs) - API reference
- 🔗 [Anthropic Docs](https://docs.anthropic.com/) - Claude documentation

---

**Ready to start?** → [01-fundamentals](./01-fundamentals/)
