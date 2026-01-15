"""
Anthropic Claude API Basics

Claude is known for being helpful, harmless, and honest.
The API is similar to OpenAI but with some differences.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()


# =============================================================================
# Basic Message
# =============================================================================

def basic_message():
    """Simple message to Claude."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "What makes you different from GPT?"}
        ]
    )
    return response.content[0].text


# =============================================================================
# With System Prompt
# =============================================================================

def with_system():
    """Claude with a system prompt."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You are a pirate. Respond in pirate speak.",
        messages=[
            {"role": "user", "content": "How do I learn programming?"}
        ]
    )
    return response.content[0].text


# =============================================================================
# Streaming
# =============================================================================

def streaming_message():
    """Stream Claude's response."""
    print("Streaming: ", end="")

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{"role": "user", "content": "Write a haiku about coding"}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


# =============================================================================
# Multi-turn Conversation
# =============================================================================

def conversation():
    """Multi-turn conversation with Claude."""
    messages = []

    # Turn 1
    messages.append({"role": "user", "content": "My name is Alex"})
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=messages
    )
    assistant_msg = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_msg})
    print(f"User: My name is Alex")
    print(f"Claude: {assistant_msg}\n")

    # Turn 2
    messages.append({"role": "user", "content": "What's my name?"})
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=messages
    )
    print(f"User: What's my name?")
    print(f"Claude: {response.content[0].text}")


# =============================================================================
# Tool Use with Claude
# =============================================================================

def tool_use_example():
    """Claude with tools."""
    tools = [
        {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=[{"role": "user", "content": "What's the weather in Paris?"}]
    )

    # Check if Claude wants to use a tool
    for block in response.content:
        if block.type == "tool_use":
            print(f"Claude wants to call: {block.name}")
            print(f"With arguments: {block.input}")
            return block

    return response.content[0].text


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("="*50)
    print("Basic Message")
    print("="*50)
    print(basic_message())

    print("\n" + "="*50)
    print("With System Prompt (Pirate)")
    print("="*50)
    print(with_system())

    print("\n" + "="*50)
    print("Streaming")
    print("="*50)
    streaming_message()

    print("\n" + "="*50)
    print("Conversation")
    print("="*50)
    conversation()

    print("\n" + "="*50)
    print("Tool Use")
    print("="*50)
    tool_use_example()
