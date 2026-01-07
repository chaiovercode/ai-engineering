# OpenAI Agents SDK

https://openai.github.io/openai-agents-python/

This is a lightweight SDK for building agentic AI apps. Few abstractions. Very little to learn. It's basically what Swarm wanted to be when it grew up.

The primitives are simple:

- **Agents**: LLMs with instructions and tools
- **Handoffs**: Let agents delegate to other agents (because sometimes even AI needs to ask for help)
- **Guardrails**: Validate inputs and outputs before things go sideways
- **Sessions**: Automatic conversation history, so you don't have to manage state yourself

That's it. Four things.

Combined with Python, these are enough to build genuinely complex systems. No steep learning curve. No framework-brain required. Just... building things.

The SDK also comes with built-in tracing. You can see what your agents are doing, debug the weird stuff, and even fine-tune models for your specific use case.

## Why use it?

Two design principles drove this thing:

1. Enough features to be worth using. Few enough to learn in an afternoon.
2. Works great out of the box. But you can change anything.

Here's what you get:

**Agent loop**: The SDK handles calling tools, sending results back to the LLM, and looping until the model is done. You don't have to write that yourself. (You're welcome.)

**Python-first**: Use actual Python to orchestrate your agents. No new abstractions to memorize. Just... Python.

**Handoffs**: Coordinate between multiple agents. One agent can hand off to another when it's out of its depth. Very human, really.

**Guardrails**: Run input validations in parallel with your agents. If a check fails, everything stops early. Before the damage is done.

**Sessions**: Conversation history just works. No manual state handling. It remembers, so you don't have to.

**Function tools**: Turn any Python function into a tool. Automatic schema generation. Pydantic validation. It's almost too easy.

**Tracing**: See what's happening. Debug the mysteries. Monitor your workflows. Use OpenAI's evaluation and fine-tuning tools if you want.

## Installation

```
pip install openai-agents
```

## Hello world

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
```

(Set your `OPENAI_API_KEY` environment variable first. Otherwise nothing works. Obviously.)

```
export OPENAI_API_KEY=sk-...
```
