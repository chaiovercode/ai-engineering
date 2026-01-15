"""
Tool Use - The Most Important Agent Pattern

This is what makes AI agents actually useful. Instead of just generating text,
agents can call functions to interact with the real world.

How it works:
1. You define tools (functions) the AI can use
2. AI decides when to call them based on the user's request
3. You execute the function and return results
4. AI uses the results to form its response
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# STEP 1: Define your tools
# =============================================================================
# Tools are just regular Python functions

def get_weather(city: str) -> dict:
    """Get current weather for a city (simulated)."""
    # In production, this would call a real weather API
    weather_data = {
        "new york": {"temp": 22, "condition": "sunny"},
        "london": {"temp": 15, "condition": "cloudy"},
        "tokyo": {"temp": 28, "condition": "humid"},
    }
    return weather_data.get(city.lower(), {"temp": 20, "condition": "unknown"})


def search_web(query: str) -> str:
    """Search the web (simulated)."""
    # In production, this would call a search API
    return f"Top results for '{query}': [Article 1], [Article 2], [Article 3]"


def calculate(expression: str) -> float:
    """Safely evaluate a math expression."""
    # Only allow safe math operations
    allowed = set("0123456789+-*/.(). ")
    if all(c in allowed for c in expression):
        return eval(expression)
    return "Invalid expression"


# =============================================================================
# STEP 2: Define tool schemas for the AI
# =============================================================================
# This tells the AI what tools exist and how to use them

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. 'New York'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression like '2 + 2' or '100 * 0.15'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


# =============================================================================
# STEP 3: The Agent Loop
# =============================================================================
# This is the core pattern - call AI, execute tools, repeat

def run_agent(user_message: str):
    """Run the agent with tool use capability."""

    print(f"\n{'='*60}")
    print(f"User: {user_message}")
    print('='*60)

    messages = [{"role": "user", "content": user_message}]

    # Map function names to actual functions
    available_functions = {
        "get_weather": get_weather,
        "search_web": search_web,
        "calculate": calculate,
    }

    # Agent loop - keep going until AI gives a final response
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"  # AI decides when to use tools
        )

        assistant_message = response.choices[0].message

        # Check if AI wants to use a tool
        if assistant_message.tool_calls:
            # Add the assistant's message to history
            messages.append(assistant_message)

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"\n🔧 Calling tool: {function_name}({function_args})")

                # Execute the function
                function = available_functions[function_name]
                result = function(**function_args)

                print(f"   Result: {result}")

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result) if isinstance(result, dict) else str(result)
                })
        else:
            # No tool calls - AI is giving its final response
            print(f"\n🤖 Agent: {assistant_message.content}")
            return assistant_message.content


if __name__ == "__main__":
    # Test different scenarios
    run_agent("What's the weather like in Tokyo?")
    run_agent("What's 15% of 250?")
    run_agent("What's the weather in London and New York? Which is warmer?")
