"""
ReAct Agent - Reasoning + Acting

The pattern behind autonomous agents. The AI thinks out loud,
decides what action to take, observes the result, and repeats.

Pattern:
1. Thought: AI reasons about what to do
2. Action: AI calls a tool
3. Observation: Result of the action
4. Repeat until task is complete
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# Tools for the agent
# =============================================================================

def search(query: str) -> str:
    """Search for information (simulated)."""
    fake_results = {
        "python creator": "Python was created by Guido van Rossum in 1991.",
        "eiffel tower height": "The Eiffel Tower is 330 meters tall.",
        "largest ocean": "The Pacific Ocean is the largest, covering 165.2 million km².",
    }
    for key, value in fake_results.items():
        if key in query.lower():
            return value
    return f"No specific results found for: {query}"


def calculator(expression: str) -> str:
    """Calculate a math expression."""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "Error: Invalid expression"


def get_current_date() -> str:
    """Get today's date."""
    from datetime import date
    return date.today().isoformat()


tools = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search for factual information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform math calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get today's date",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

available_tools = {
    "search": search,
    "calculator": calculator,
    "get_current_date": get_current_date
}


# =============================================================================
# ReAct Agent Implementation
# =============================================================================

REACT_SYSTEM_PROMPT = """You are a helpful assistant that solves problems step by step.

For each step:
1. Think about what you need to do
2. Use a tool if needed
3. Analyze the result
4. Continue until you have the final answer

Always explain your reasoning before taking actions."""


def react_agent(task: str, max_steps: int = 5) -> str:
    """
    Run a ReAct agent that thinks, acts, and observes.
    """
    print(f"\n{'='*70}")
    print(f"🎯 Task: {task}")
    print('='*70)

    messages = [
        {"role": "system", "content": REACT_SYSTEM_PROMPT},
        {"role": "user", "content": task}
    ]

    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Print the agent's thinking (if any text response)
        if assistant_message.content:
            print(f"💭 Thought: {assistant_message.content}")

        # Check if agent wants to use tools
        if assistant_message.tool_calls:
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"🔧 Action: {func_name}({func_args})")

                # Execute tool
                result = available_tools[func_name](**func_args)

                print(f"👁️ Observation: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            # No tool calls = agent is done
            print(f"\n✅ Final Answer: {assistant_message.content}")
            return assistant_message.content

    return "Max steps reached without completion"


# =============================================================================
# Examples
# =============================================================================

if __name__ == "__main__":
    # Simple query
    react_agent("Who created Python and in what year?")

    # Multi-step reasoning
    react_agent("How tall is the Eiffel Tower in feet? (1 meter = 3.28 feet)")

    # Complex task requiring multiple tools
    react_agent("What's today's date, and how many days until New Year 2026?")
