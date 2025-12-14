# AI Agents Foundations

Learn the 8 core patterns for building production-ready AI agents.

## Quick Start

```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-key-here" > .env
python complete_tutorial.py
```

## The 8 Patterns

1. **Basic LLM Calls** - Understanding statelessness
2. **Conversation Chaining** - Building multi-turn conversations
3. **LLM Orchestration** - Multiple LLMs working together
4. **RAG** - Document-based context instead of fine-tuning
5. **Tool Use** ⭐ - Most important! Makes agents actually useful
6. **Evaluation** - Quality control with a second LLM
7. **Production Agent Class** - Clean, deployable architecture
8. **Autonomous Agents** - Self-directed (use with caution)

## Files

- `complete_tutorial.py` - Working demos of all 7 patterns (not #8)
- `agents/career_agent.py` - Personal AI assistant (RAG + Tools)
- `agents/support_agent.py` - Customer support (Evaluation + Retry)
- `agents/research_agent.py` - Multi-agent researcher (Orchestration)

## Run a Production Agent

```bash
python agents/career_agent.py
```

Open http://127.0.0.1:7860

## What You'll Learn

- How LLMs are stateless (no memory between calls)
- The tool execution loop (foundation of all agents)
- RAG vs fine-tuning
- Why evaluation is critical for production
- When NOT to use autonomous agents

Run `complete_tutorial.py` first, then study the 3 production agents.
