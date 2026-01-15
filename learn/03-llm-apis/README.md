# LLM APIs

> Talk to AI with code.

## What is an LLM API?

An **API** (Application Programming Interface) lets your code talk to an LLM.

Instead of typing in ChatGPT, your program sends messages and gets responses.

```
Your Code                     LLM Provider
    │                              │
    │  "What's 2+2?"               │
    │ ──────────────────────────►  │
    │                              │
    │  "4"                         │
    │ ◄──────────────────────────  │
```

---

## The Two Big Players

### OpenAI (GPT-4, GPT-4o)
- Most popular
- Best for general tasks
- ChatGPT is built on this

### Anthropic (Claude)
- Known for being helpful and safe
- Great at long documents
- Strong at coding tasks

---

## Your First API Call

### OpenAI

```python
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY from environment

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
# Output: "Paris"
```

### Anthropic (Claude)

```python
from anthropic import Anthropic

client = Anthropic()  # Uses ANTHROPIC_API_KEY from environment

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.content[0].text)
# Output: "Paris"
```

---

## Understanding the Message Format

Both APIs use a **conversation format** with roles:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant"},  # AI's personality
    {"role": "user", "content": "Hi!"},                            # User message
    {"role": "assistant", "content": "Hello! How can I help?"},    # AI's response
    {"role": "user", "content": "What's the weather?"},            # Another user message
]
```

**Roles:**
- `system` - Instructions for how the AI should behave
- `user` - Messages from the human
- `assistant` - Previous AI responses (for context)

---

## Streaming (Real-Time Responses)

Instead of waiting for the complete response, get it word by word:

```python
# Without streaming - wait for everything
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a story"}]
)
print(response.choices[0].message.content)  # Prints all at once

# With streaming - see it as it's generated
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)
for chunk in stream:
    print(chunk.choices[0].delta.content, end="")  # Prints word by word
```

**Why streaming?**
- Better user experience (they see progress)
- Can show a "typing" indicator
- Users don't stare at a blank screen

---

## JSON Mode (Structured Output)

Force the AI to respond with valid JSON:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "List 3 fruits as JSON: {\"fruits\": [...]}"
    }],
    response_format={"type": "json_object"}  # Forces valid JSON
)

import json
data = json.loads(response.choices[0].message.content)
print(data["fruits"])  # ['apple', 'banana', 'orange']
```

---

## Embeddings (Turn Text into Numbers)

**Embeddings** convert text into numbers that represent meaning.

Similar meanings = similar numbers.

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="I love pizza"
)

vector = response.data[0].embedding
# [0.023, -0.045, 0.012, ...]  (1536 numbers)
```

**Why embeddings?**
- Search for similar content
- Build recommendation systems
- Power RAG (Retrieval Augmented Generation)

```
"I love pizza"     →  [0.1, 0.2, 0.3, ...]
"Pizza is great"   →  [0.1, 0.2, 0.3, ...]  ← Similar numbers!
"I hate mornings"  →  [0.9, -0.1, 0.5, ...]  ← Different numbers
```

---

## Vision (Understanding Images)

GPT-4o can see and understand images:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}}
        ]
    }]
)

print(response.choices[0].message.content)
# "This image shows an orange tabby cat sitting on a windowsill..."
```

---

## Cost and Pricing

You pay per **token** (roughly per word):

| Model | Input Cost | Output Cost |
|-------|------------|-------------|
| GPT-4o-mini | $0.15/1M tokens | $0.60/1M tokens |
| GPT-4o | $2.50/1M tokens | $10/1M tokens |
| Claude Sonnet | $3/1M tokens | $15/1M tokens |

**Rough estimate:** 1,000 tokens ≈ 750 words ≈ $0.001-0.01

---

## Environment Setup

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Load in Python:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file

# Now the API clients automatically use these keys
```

---

## Quick Comparison

| Feature | OpenAI | Anthropic |
|---------|--------|-----------|
| Models | GPT-4, GPT-4o, GPT-4o-mini | Claude Opus, Sonnet, Haiku |
| Streaming | ✅ | ✅ |
| JSON mode | ✅ | ✅ |
| Vision | ✅ GPT-4o | ✅ Claude 3+ |
| Embeddings | ✅ | ❌ (use Voyage AI) |
| Max context | 128K tokens | 200K tokens |

---

## Error Handling

APIs can fail. Always handle errors:

```python
from openai import OpenAI, APIError, RateLimitError

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}]
    )
except RateLimitError:
    print("Too many requests! Wait and try again.")
except APIError as e:
    print(f"API error: {e}")
```

---

## Try It Yourself

```bash
cd 03-llm-apis
pip install -r requirements.txt

# Set your API keys
export OPENAI_API_KEY=your-key-here

# Run examples
python openai_basics.py
python anthropic_basics.py
```

---

## Key Takeaways

1. **APIs let code talk to LLMs** - Send messages, get responses
2. **Use streaming** - Better user experience
3. **JSON mode** - Get structured, parseable data
4. **Embeddings** - Convert text to numbers for search
5. **Handle errors** - APIs can fail, be prepared

---

## Next Steps

→ [04-agents](../04-agents/) - Build AI that can take actions
