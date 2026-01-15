# AI Engineering

Learning to build production-ready AI systems from scratch.

## Learning Modules

**[01-fundamentals](learn/01-fundamentals/)** — Core concepts and building blocks

**[02-prompt-engineering](learn/02-prompt-engineering/)** — Prompt design techniques

**[03-llm-apis](learn/03-llm-apis/)** — Working with OpenAI and Anthropic APIs

**[04-agents](learn/04-agents/)** — Agent patterns: tool use, RAG, ReAct, evaluation, production

**[05-orchestration](learn/05-orchestration/)** — Multi-agent pipelines with LangGraph

**[06-observability](learn/06-observability/)** — LangSmith tracing, custom instrumentation, evaluation

## Apps

**[research-app](apps/research-app/)** — Full-stack research assistant with LangGraph backend and Next.js frontend

**[aqi-cards](apps/aqi-cards/)** — Air quality data visualization

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install openai anthropic langchain langgraph langsmith python-dotenv

# Set up API keys in .env
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
LANGSMITH_API_KEY=...
```
