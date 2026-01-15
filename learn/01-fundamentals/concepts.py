"""
AI Engineering Fundamentals

This module covers the core concepts you need to understand
before building AI applications.

Key Concepts:
- What is an LLM (Large Language Model)?
- Tokens and context windows
- Temperature and sampling
- System prompts vs user prompts
- Completion vs Chat models
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# CONCEPT 1: Basic Chat Completion
# =============================================================================
# This is the most fundamental operation - sending a message and getting a response

def basic_completion():
    """The simplest possible LLM call."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What is AI engineering in one sentence?"}
        ]
    )
    return response.choices[0].message.content


# =============================================================================
# CONCEPT 2: System Prompts
# =============================================================================
# System prompts set the behavior and personality of the AI

def with_system_prompt():
    """System prompts define HOW the AI should behave."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a senior engineer who explains things simply. Use analogies."
            },
            {
                "role": "user",
                "content": "What is a neural network?"
            }
        ]
    )
    return response.choices[0].message.content


# =============================================================================
# CONCEPT 3: Temperature
# =============================================================================
# Temperature controls randomness: 0 = deterministic, 1 = creative

def temperature_comparison():
    """Compare low vs high temperature outputs."""
    prompt = "Give me a creative name for a coffee shop"

    # Low temperature - more predictable
    low_temp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    # High temperature - more creative/random
    high_temp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )

    return {
        "low_temp": low_temp.choices[0].message.content,
        "high_temp": high_temp.choices[0].message.content
    }


# =============================================================================
# CONCEPT 4: Conversation History
# =============================================================================
# LLMs are stateless - you must send the full conversation each time

def conversation_with_memory():
    """LLMs don't remember - you manage the conversation history."""
    messages = [
        {"role": "system", "content": "You are a helpful tutor."},
        {"role": "user", "content": "My name is Alex. I want to learn Python."},
    ]

    # First response
    response1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Add assistant's response to history
    messages.append({
        "role": "assistant",
        "content": response1.choices[0].message.content
    })

    # Add follow-up question
    messages.append({
        "role": "user",
        "content": "What should I learn first?"
    })

    # Second response - AI now has context of the full conversation
    response2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return response2.choices[0].message.content


# =============================================================================
# CONCEPT 5: Tokens and Limits
# =============================================================================
# Tokens are the units LLMs process - roughly 4 chars per token

def understand_tokens():
    """See how text gets tokenized."""
    import tiktoken

    encoder = tiktoken.encoding_for_model("gpt-4o-mini")

    text = "AI Engineering is the practice of building applications with LLMs."
    tokens = encoder.encode(text)

    return {
        "text": text,
        "token_count": len(tokens),
        "tokens": [encoder.decode([t]) for t in tokens]
    }


if __name__ == "__main__":
    print("=" * 50)
    print("CONCEPT 1: Basic Completion")
    print("=" * 50)
    print(basic_completion())

    print("\n" + "=" * 50)
    print("CONCEPT 2: System Prompts")
    print("=" * 50)
    print(with_system_prompt())

    print("\n" + "=" * 50)
    print("CONCEPT 3: Temperature")
    print("=" * 50)
    temps = temperature_comparison()
    print(f"Low temp (0.1): {temps['low_temp']}")
    print(f"High temp (1.0): {temps['high_temp']}")

    print("\n" + "=" * 50)
    print("CONCEPT 4: Conversation Memory")
    print("=" * 50)
    print(conversation_with_memory())
