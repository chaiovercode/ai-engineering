# AI Fundamentals

> Start here if you're new to AI engineering.

## What is an LLM?

**LLM** stands for **Large Language Model**. Think of it as a very smart autocomplete.

When you type a message, the LLM predicts "what text should come next?" based on patterns it learned from reading billions of web pages, books, and articles.

```
You type:  "The capital of France is"
LLM adds:  "Paris"
```

That's it. At its core, an LLM is just predicting the next word, over and over.

---

## The 5 Key Concepts

### 1. LLMs Have No Memory

This is the most important thing to understand.

**Every time you send a message, the LLM starts fresh.** It doesn't remember your previous conversations.

```
Message 1: "My name is Sarah"
Response:  "Nice to meet you, Sarah!"

Message 2: "What's my name?"
Response:  "I don't know your name."  ← It forgot!
```

**How chatbots "remember":** They cheat! They send the ENTIRE conversation history with every message.

```
Actual Message 2 sent to LLM:
- User: "My name is Sarah"
- Assistant: "Nice to meet you, Sarah!"
- User: "What's my name?"

Now the LLM can see the whole conversation and answer correctly.
```

---

### 2. Tokens (How LLMs Read Text)

LLMs don't read letters or words. They read **tokens**.

A token is roughly 3-4 characters or about 0.75 words.

```
"Hello world" = 2 tokens
"Artificial intelligence" = 2 tokens
"I love programming in Python!" = 6 tokens
```

**Why this matters:**
- LLMs have a **token limit** (like 128,000 tokens)
- You pay per token (input + output)
- Longer conversations = more expensive

---

### 3. Context Window (The LLM's Working Memory)

The **context window** is how much text the LLM can "see" at once.

Think of it like a desk. You can only fit so many papers on your desk at once.

```
GPT-4o: ~128,000 tokens (a small novel)
Claude: ~200,000 tokens (a large novel)
```

If your conversation gets too long, older messages get "pushed off the desk" and forgotten.

---

### 4. Temperature (Creativity vs Consistency)

**Temperature** controls how random/creative the LLM's responses are.

```
Temperature 0.0 = Very predictable, same answer every time
Temperature 1.0 = Creative, different answers each time
```

**When to use what:**

| Temperature | Use Case |
|-------------|----------|
| 0.0 - 0.3 | Facts, code, math, data extraction |
| 0.4 - 0.7 | General conversations, explanations |
| 0.8 - 1.0 | Creative writing, brainstorming |

---

### 5. System Prompt vs User Prompt

Messages to LLMs come in different types:

**System Prompt** (The AI's personality/instructions)
```
"You are a helpful cooking assistant. Give recipes in simple steps."
```

**User Prompt** (What the user actually asks)
```
"How do I make pasta?"
```

The system prompt is like giving the AI a job description before it starts working.

---

## Putting It Together

Here's what happens when you chat with an AI:

```
┌─────────────────────────────────────────────┐
│              YOUR MESSAGE                    │
│  "How do I make pancakes?"                  │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         WHAT'S ACTUALLY SENT                │
│                                             │
│  System: "You are a cooking assistant..."   │
│  Previous messages (if any)                 │
│  User: "How do I make pancakes?"            │
│                                             │
│  Settings: temperature=0.7, model=gpt-4     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│              LLM PROCESSES                   │
│                                             │
│  1. Converts text to tokens                 │
│  2. Predicts best response                  │
│  3. Converts tokens back to text            │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│              RESPONSE                        │
│  "Here's a simple pancake recipe..."        │
└─────────────────────────────────────────────┘
```

---

## Common Mistakes Beginners Make

| Mistake | Reality |
|---------|---------|
| "The AI remembers me" | No, you're sending history each time |
| "AI knows current events" | No, it only knows up to its training date |
| "AI is always right" | No, it confidently makes up things (hallucination) |
| "Longer prompts = better" | No, clear and concise often works better |

---

## Try It Yourself

Run the example code:

```bash
cd 01-fundamentals
pip install -r requirements.txt
python concepts.py
```

This will demonstrate:
- Basic LLM calls
- System prompts in action
- Temperature differences
- Conversation memory

---

## Key Takeaways

1. **LLMs predict text** - They're smart autocomplete
2. **No memory** - You manage conversation history
3. **Tokens matter** - They affect cost and limits
4. **Temperature controls creativity** - Low = consistent, High = creative
5. **System prompts shape behavior** - Like giving AI a job description

---

## Next Steps

Once you understand these basics, move to:
→ [02-prompt-engineering](../02-prompt-engineering/) - Learn how to get better responses
