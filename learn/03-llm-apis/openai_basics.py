"""
OpenAI API Basics

The most commonly used LLM API. This covers:
- Chat completions
- Streaming responses
- JSON mode
- Vision (image understanding)
"""

import os
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# Basic Chat Completion
# =============================================================================

def basic_chat():
    """Simple chat completion."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the capital of Japan?"}
        ]
    )
    return response.choices[0].message.content


# =============================================================================
# Streaming Responses
# =============================================================================

def streaming_chat():
    """Stream the response token by token."""
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Count from 1 to 10 slowly"}],
        stream=True
    )

    print("Streaming: ", end="")
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    print()  # New line
    return full_response


# =============================================================================
# JSON Mode
# =============================================================================

def json_response():
    """Force the model to return valid JSON."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "List 3 programming languages with their creators as JSON"
        }],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


# =============================================================================
# Vision - Understanding Images
# =============================================================================

def describe_image_from_url(image_url: str):
    """Describe an image from URL."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }]
    )
    return response.choices[0].message.content


def describe_local_image(image_path: str):
    """Describe a local image file."""
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }]
    )
    return response.choices[0].message.content


# =============================================================================
# Embeddings - Turn text into vectors
# =============================================================================

def get_embedding(text: str) -> list[float]:
    """Convert text to a vector (for similarity search)."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts."""
    import numpy as np

    emb1 = np.array(get_embedding(text1))
    emb2 = np.array(get_embedding(text2))

    return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("="*50)
    print("Basic Chat")
    print("="*50)
    print(basic_chat())

    print("\n" + "="*50)
    print("Streaming")
    print("="*50)
    streaming_chat()

    print("\n" + "="*50)
    print("JSON Mode")
    print("="*50)
    print(json_response())

    print("\n" + "="*50)
    print("Embeddings & Similarity")
    print("="*50)
    texts = [
        "I love programming in Python",
        "Python is my favorite language",
        "The weather is nice today"
    ]
    print(f"Text 1 vs Text 2: {similarity(texts[0], texts[1]):.3f}")
    print(f"Text 1 vs Text 3: {similarity(texts[0], texts[2]):.3f}")
