"""
Prompt Engineering Techniques

Learn how to write effective prompts that get better results from LLMs.

Techniques covered:
1. Zero-shot prompting
2. Few-shot prompting (examples)
3. Chain of thought (step-by-step reasoning)
4. Structured output (JSON)
5. Role prompting
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# TECHNIQUE 1: Zero-Shot Prompting
# =============================================================================
# Just ask directly - no examples provided

def zero_shot():
    """Direct question without examples."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "Classify this review as positive or negative: 'The food was cold and the service was slow.'"
        }]
    )
    return response.choices[0].message.content


# =============================================================================
# TECHNIQUE 2: Few-Shot Prompting
# =============================================================================
# Provide examples to guide the model's behavior

def few_shot():
    """Provide examples to improve accuracy."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": """Classify reviews as positive or negative.

Examples:
- "Amazing experience, will come back!" -> positive
- "Terrible, never again." -> negative
- "Best purchase I've made!" -> positive

Now classify: "The food was cold and the service was slow."
"""
        }]
    )
    return response.choices[0].message.content


# =============================================================================
# TECHNIQUE 3: Chain of Thought
# =============================================================================
# Ask the model to think step by step

def chain_of_thought():
    """Step-by-step reasoning improves accuracy on complex tasks."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": """Solve this problem step by step:

A store sells apples for $2 each. If you buy 5 or more, you get 20% off.
How much would 7 apples cost?

Think through this step by step before giving the final answer."""
        }]
    )
    return response.choices[0].message.content


# =============================================================================
# TECHNIQUE 4: Structured Output (JSON)
# =============================================================================
# Get predictable, parseable responses

def structured_output():
    """Request JSON output for easier parsing."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a data extraction assistant. Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": """Extract information from this text and return as JSON:

"John Smith is a 32-year-old software engineer from San Francisco.
He has 8 years of experience and specializes in Python and machine learning."

Return: {"name": "", "age": 0, "job": "", "location": "", "skills": []}"""
            }
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


# =============================================================================
# TECHNIQUE 5: Role Prompting
# =============================================================================
# Give the AI a specific persona for better domain responses

def role_prompting():
    """Assign a role for domain-specific expertise."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a senior software architect with 20 years of experience.
You give practical, battle-tested advice based on real-world experience.
You mention trade-offs and when NOT to use certain approaches."""
            },
            {
                "role": "user",
                "content": "Should I use microservices for my new startup's MVP?"
            }
        ]
    )
    return response.choices[0].message.content


# =============================================================================
# TECHNIQUE 6: Delimiter-Based Prompting
# =============================================================================
# Use clear delimiters to separate instructions from content

def delimiter_prompting():
    """Use delimiters to clearly separate content from instructions."""
    user_content = """
I bought this laptop last week and I'm really disappointed.
The battery only lasts 2 hours and the screen has dead pixels.
Customer support was unhelpful. Would not recommend.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""Analyze the customer review below and extract:
1. Main complaints (as a list)
2. Sentiment score (1-10)
3. Recommended action for the company

---REVIEW START---
{user_content}
---REVIEW END---

Respond in a structured format."""
        }]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("=" * 60)
    print("TECHNIQUE 1: Zero-Shot")
    print("=" * 60)
    print(zero_shot())

    print("\n" + "=" * 60)
    print("TECHNIQUE 2: Few-Shot (with examples)")
    print("=" * 60)
    print(few_shot())

    print("\n" + "=" * 60)
    print("TECHNIQUE 3: Chain of Thought")
    print("=" * 60)
    print(chain_of_thought())

    print("\n" + "=" * 60)
    print("TECHNIQUE 4: Structured Output (JSON)")
    print("=" * 60)
    print(json.dumps(structured_output(), indent=2))

    print("\n" + "=" * 60)
    print("TECHNIQUE 5: Role Prompting")
    print("=" * 60)
    print(role_prompting())

    print("\n" + "=" * 60)
    print("TECHNIQUE 6: Delimiter Prompting")
    print("=" * 60)
    print(delimiter_prompting())
