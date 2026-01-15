# AI Agents

> AI that can actually DO things.

## What is an AI Agent?

A regular LLM just generates text.

An **AI Agent** can take actions in the real world.

```
Regular LLM:
User: "What's the weather in Tokyo?"
AI: "I don't have access to real-time weather data."

AI Agent:
User: "What's the weather in Tokyo?"
AI: *checks weather API* "It's 24°C and sunny in Tokyo right now."
```

The difference? The agent has **tools** it can use.

---

## The Big Idea: Tools

**Tools** are functions the AI can call.

```
┌─────────────────────────────────────────────────────┐
│                    AI AGENT                          │
│                                                      │
│  Brain (LLM)  ←──────→  Tools                       │
│    │                      │                          │
│    │                      ├── get_weather()          │
│    │                      ├── search_web()           │
│    │                      ├── send_email()           │
│    │                      └── calculate()            │
└─────────────────────────────────────────────────────┘
```

The AI decides:
1. "Do I need a tool for this?"
2. "Which tool should I use?"
3. "What inputs do I give it?"

---

## How Tool Use Works

**Step 1:** You define tools the AI can use

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "city": "The city name"
        }
    }
]
```

**Step 2:** User asks something

```
"What's the weather in Paris?"
```

**Step 3:** AI decides to use a tool

```
AI thinks: "I need weather info. I'll use get_weather."
AI calls: get_weather(city="Paris")
```

**Step 4:** You run the function and return the result

```python
result = get_weather("Paris")  # Returns: {"temp": 18, "condition": "cloudy"}
```

**Step 5:** AI uses the result to respond

```
"It's 18°C and cloudy in Paris right now."
```

---

## The Agent Loop

Agents work in a loop:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│    ┌─────────────┐                                       │
│    │  User asks  │                                       │
│    │  question   │                                       │
│    └──────┬──────┘                                       │
│           │                                              │
│           ▼                                              │
│    ┌─────────────┐      ┌─────────────┐                 │
│    │  AI thinks  │─────►│  Need tool? │                 │
│    └─────────────┘      └──────┬──────┘                 │
│                                │                         │
│              ┌─────────────────┴─────────────────┐      │
│              │                                   │      │
│              ▼                                   ▼      │
│       ┌────────────┐                    ┌────────────┐  │
│       │  YES: Use  │                    │  NO: Give  │  │
│       │   tool     │                    │  answer    │  │
│       └─────┬──────┘                    └────────────┘  │
│             │                                           │
│             ▼                                           │
│       ┌────────────┐                                    │
│       │  Run tool  │                                    │
│       │  get result│                                    │
│       └─────┬──────┘                                    │
│             │                                           │
│             └──────────────► (back to AI thinks)        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

The AI keeps looping until it has enough info to answer.

---

## The 5 Key Patterns

### 1. Tool Use (Most Important!)

AI can call functions you define.

```python
# You define this
def search_web(query):
    return google.search(query)

# AI decides to use it
AI: "I need to search for info about Python 3.12"
AI calls: search_web("Python 3.12 new features")
```

**Use for:** Any action the AI needs to take (search, send, calculate, lookup)

---

### 2. RAG (Retrieval Augmented Generation)

Give AI access to YOUR documents without retraining.

```
User: "What's our company's refund policy?"

Without RAG:
AI: "I don't know your specific policy..."

With RAG:
1. Search your documents for "refund policy"
2. Find: "Refunds within 30 days, original packaging required"
3. AI: "Your refund policy allows returns within 30 days
        if items are in original packaging."
```

**Use for:** Chatbots that know about your data (docs, policies, products)

---

### 3. ReAct (Reasoning + Acting)

AI thinks out loud, then acts.

```
User: "What's the population of the capital of France?"

AI Thought: "I need to find the capital of France first."
AI Action: search("capital of France")
AI Observation: "Paris is the capital of France"

AI Thought: "Now I need Paris's population."
AI Action: search("population of Paris")
AI Observation: "Paris has about 2.1 million people"

AI Answer: "Paris, the capital of France, has about 2.1 million people."
```

**Use for:** Complex questions that need multiple steps.

---

### 4. Evaluation (AI Judging AI)

Use one AI to check another AI's work.

```
# AI 1 generates an answer
answer = ai1.generate("Explain quantum computing")

# AI 2 evaluates the answer
evaluation = ai2.evaluate(
    question="Explain quantum computing",
    answer=answer,
    criteria=["accuracy", "clarity", "completeness"]
)

# Result: {"accuracy": 0.9, "clarity": 0.8, "completeness": 0.7}
```

**Use for:** Quality control, automated testing, grading.

---

### 5. Production Agent (Putting It All Together)

A complete, reusable agent class:

```python
agent = Agent(
    name="Customer Support",
    system_prompt="You are a helpful support agent...",
    tools=[lookup_order, check_inventory, create_ticket]
)

response = agent.run("Where is my order #12345?")
# Agent uses lookup_order tool, then responds with status
```

---

## Simple Agent Example

```python
# Define a tool
def calculate(expression):
    return eval(expression)  # Careful: only for demo!

# Tell AI about the tool
tools = [{
    "name": "calculate",
    "description": "Do math calculations",
    "parameters": {"expression": "Math like '2+2' or '10*5'"}
}]

# User asks something
user_message = "What's 15% of 200?"

# AI decides to use calculator
# AI calls: calculate("200 * 0.15")
# Result: 30

# AI responds: "15% of 200 is 30"
```

---

## RAG in Simple Terms

Think of RAG like giving the AI a book to reference:

```
Without RAG (AI's memory only):
┌─────────────────────────────────────────┐
│  User: "What's in Chapter 5?"           │
│  AI: "I haven't read your book..."      │
└─────────────────────────────────────────┘

With RAG (AI can search documents):
┌─────────────────────────────────────────┐
│  User: "What's in Chapter 5?"           │
│                                         │
│  1. Search documents for "Chapter 5"    │
│  2. Find: "Chapter 5 discusses..."      │
│  3. AI reads the found content          │
│  4. AI: "Chapter 5 covers..."           │
└─────────────────────────────────────────┘
```

---

## Common Agent Tools

| Tool | What It Does | Example |
|------|--------------|---------|
| Web Search | Find information online | "Search for Python tutorials" |
| Calculator | Do math | "What's 18% tip on $45?" |
| Database | Query your data | "Find orders from last week" |
| Email | Send messages | "Send report to team" |
| Calendar | Check/create events | "What meetings do I have today?" |
| File System | Read/write files | "Save this to notes.txt" |

---

## The Hallucination Problem

**Hallucination** = AI confidently making things up.

```
User: "How many goals did Messi score in 2023?"
AI: "Messi scored 47 goals in 2023."  ← Made up number!
```

**How agents help:** They can verify with tools.

```
User: "How many goals did Messi score in 2023?"
Agent: *searches web* "According to recent stats,
        Messi scored 32 goals in 2023."
```

---

## Try It Yourself

```bash
cd 04-agents
pip install -r requirements.txt

# Run examples
python 01_tool_use.py      # Basic tool usage
python 02_rag.py           # Document Q&A
python 03_react_agent.py   # Think-then-act
python 04_evaluation.py    # AI judging AI
python 05_production_agent.py  # Complete agent
```

---

## Key Takeaways

1. **Agents = LLM + Tools** - AI that can take actions
2. **Tool Use is fundamental** - Define functions AI can call
3. **RAG grounds answers** - AI references your documents
4. **ReAct = Think + Act** - Step-by-step reasoning
5. **Evaluate everything** - Use AI to check AI's work

---

## Next Steps

→ [05-orchestration](../05-orchestration/) - Coordinate multiple agents
