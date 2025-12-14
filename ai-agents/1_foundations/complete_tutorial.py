"""
AI AGENTS FOUNDATIONS - COMPLETE TUTORIAL
==========================================

This file demonstrates the 7 core patterns you need to build production AI agents:

1. Basic LLM Calls — Understanding statelessness
2. Conversation Chaining — Building multi-turn conversations
3. LLM Orchestration — Multiple LLMs working together (Generator → Workers → Judge)
4. RAG — Providing context instead of fine-tuning
5. Tool Use — The most important pattern (makes agents actually useful)
6. Evaluation — Quality control with a second LLM
7. Production Agent Class — Combining everything into deployable code

Note: Pattern 8 (Autonomous Agents) is intentionally NOT included here.
That's advanced territory with real risks. Start with these 7 first.

Run this file to see each pattern in action:
    python complete_tutorial.py

Then check out the production agents in the agents/ folder.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# Initialize
load_dotenv(override=True)
openai = OpenAI()


# ============================================================================
# PATTERN 1: BASIC LLM CALLS — The Amnesiac Genius
# ============================================================================
# Key insight: LLMs remember NOTHING between calls. You control all context.

def demo_basic_llm():
    """The simplest possible LLM interaction"""
    print("\n" + "="*70)
    print("PATTERN 1: Basic LLM Calls — The Amnesiac Genius")
    print("="*70)

    messages = [{"role": "user", "content": "What is 2+2?"}]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    print(f"Q: What is 2+2?")
    print(f"A: {response.choices[0].message.content}")

    print("\n💡 The LLM has ZERO memory. Every call is a blank slate.")
    print("   This is why you must provide full context each time.\n")


# ============================================================================
# PATTERN 2: CONVERSATION CHAINING — The Conversation Scribe
# ============================================================================
# Key insight: Keep a running transcript. Send it all back each time.

def demo_conversation_chaining():
    """Fix the amnesia problem by writing everything down"""
    print("\n" + "="*70)
    print("PATTERN 2: Conversation Chaining — The Conversation Scribe")
    print("="*70)

    # Start with empty history
    messages = []

    # First exchange
    messages.append({"role": "user", "content": "I'm thinking of a country in Europe"})
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    ai_msg = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_msg})
    print(f"User: I'm thinking of a country in Europe")
    print(f"AI: {ai_msg}\n")

    # Second exchange - AI remembers because we send the history
    messages.append({"role": "user", "content": "It has the Eiffel Tower"})
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    ai_msg = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_msg})
    print(f"User: It has the Eiffel Tower")
    print(f"AI: {ai_msg}")

    print("\n💡 The AI 'remembers' because we send the full conversation each time.")
    print("   This is how every chatbot works under the hood.\n")


# ============================================================================
# PATTERN 3: LLM ORCHESTRATION — The Creative Team
# ============================================================================
# Key insight: One model to generate, multiple to work, one to judge = better results

def demo_llm_orchestration():
    """Multiple LLMs in different roles, competing and being judged"""
    print("\n" + "="*70)
    print("PATTERN 3: LLM Orchestration — The Creative Team")
    print("="*70)

    # STEP 1: Generator creates a challenge
    print("\n[GENERATOR] Creating a logic puzzle...")
    messages = [{"role": "user", "content": "Create a short logic puzzle. Just the puzzle, nothing else."}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    puzzle = response.choices[0].message.content
    print(f"Puzzle: {puzzle[:150]}...\n")

    # STEP 2: Multiple workers solve it
    print("[WORKERS] Multiple AIs solving the puzzle...")
    solutions = []
    for i in range(2):
        messages = [{"role": "user", "content": puzzle}]
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=100)
        solution = response.choices[0].message.content
        solutions.append(solution)
        print(f"  Worker {i+1}: {solution[:80]}...")

    # STEP 3: Judge evaluates
    print("\n[JUDGE] Evaluating which solution is better...")
    judge_prompt = f"""You are judging a competition. Two AIs solved this puzzle:

Puzzle: {puzzle}

Solution 1: {solutions[0]}
Solution 2: {solutions[1]}

Which is better? Respond ONLY with JSON: {{"winner": "1" or "2", "reason": "brief explanation"}}"""

    messages = [{"role": "user", "content": judge_prompt}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    print(f"Judge: {response.choices[0].message.content}")

    print("\n💡 Generator → Workers (compete) → Judge = Better quality, lower cost")
    print("   Use cheap models for workers, expensive for judging.\n")


# ============================================================================
# PATTERN 4: RAG — The Open-Book Exam
# ============================================================================
# Key insight: Don't fine-tune. Just stuff context into the prompt.

def demo_rag_pattern():
    """Load documents and include them in the prompt"""
    print("\n" + "="*70)
    print("PATTERN 4: RAG — The Open-Book Exam")
    print("="*70)

    # Load context from files
    try:
        reader = PdfReader("me/linkedin.pdf")
        linkedin = "".join([page.extract_text() or "" for page in reader.pages])
        print(f"✅ Loaded LinkedIn PDF ({len(linkedin)} characters)")
    except:
        linkedin = "LinkedIn data not available"
        print("⚠️  No LinkedIn PDF found")

    try:
        with open("me/summary.txt", "r") as f:
            summary = f.read()
        print(f"✅ Loaded summary ({len(summary)} characters)")
    except:
        summary = "Summary not available"
        print("⚠️  No summary found")

    # Stuff it all into the system prompt (THIS IS RAG!)
    system_prompt = f"""You are answering questions about Vivek.

CONTEXT:
{summary}

{linkedin[:500]}...

Answer ONLY based on the context above. If you don't know, say so."""

    # Now ask questions
    question = "What's the person's background?"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    print(f"\nQ: {question}")
    print(f"A: {response.choices[0].message.content[:200]}...")

    print("\n💡 RAG = Load docs → Stuff into prompt → LLM answers from context")
    print("   Way cheaper and faster than fine-tuning. This is why RAG won.\n")


# ============================================================================
# PATTERN 5: TOOL USE — The Digital Handyman ⭐ MOST IMPORTANT
# ============================================================================
# Key insight: This is THE pattern that makes agents actually useful

def demo_tool_use():
    """LLM decides when to call functions. This is where the magic happens."""
    print("\n" + "="*70)
    print("PATTERN 5: Tool Use — The Digital Handyman ⭐ MOST IMPORTANT")
    print("="*70)

    # Define some tools
    def get_weather(city: str):
        """Simulated weather API"""
        weather_db = {
            "Tokyo": "72°F and sunny",
            "London": "15°C and rainy",
            "New York": "68°F and cloudy"
        }
        return weather_db.get(city, "Weather data not available")

    def save_email(email: str, name: str = "Unknown"):
        """Save user contact info"""
        print(f"  💾 Saved contact: {name} <{email}>")
        return {"status": "saved", "email": email}

    # Describe the tools to the LLM
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"}
                    },
                    "required": ["city"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "save_email",
                "description": "Save a user's email address",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "name": {"type": "string"}
                    },
                    "required": ["email"],
                    "additionalProperties": False
                }
            }
        }
    ]

    # User asks something that needs a tool
    user_message = "What's the weather in Tokyo? Also save my email: test@example.com"
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools."},
        {"role": "user", "content": user_message}
    ]

    print(f"User: {user_message}\n")

    # THE TOOL EXECUTION LOOP (this is the foundation of all agents)
    done = False
    iteration = 0
    while not done:
        iteration += 1
        print(f"[Loop iteration {iteration}]")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        finish_reason = response.choices[0].finish_reason

        if finish_reason == "tool_calls":
            # LLM wants to use tools
            message = response.choices[0].message
            tool_calls = message.tool_calls

            print(f"  🔧 LLM calling {len(tool_calls)} tool(s)...")

            # Execute each tool
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                print(f"     {tool_name}({arguments})")

                # Actually call the function
                if tool_name == "get_weather":
                    result = get_weather(**arguments)
                elif tool_name == "save_email":
                    result = save_email(**arguments)
                else:
                    result = "Unknown tool"

                # Add result back to conversation
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "content": json.dumps({"result": result}),
                    "tool_call_id": tool_call.id
                })
        else:
            # LLM has final answer
            done = True
            print(f"\nAssistant: {response.choices[0].message.content}")

    print("\n💡 This loop powers EVERYTHING. ChatGPT plugins, AI agents, all of it.")
    print("   LLM → Calls tool → Execute → Add result → Loop back → Final answer\n")


# ============================================================================
# PATTERN 6: EVALUATION — The Quality Control Inspector
# ============================================================================
# Key insight: Never trust AI output blindly. Have another AI check it.

def demo_evaluation():
    """Use a second LLM to check the first LLM's work"""
    print("\n" + "="*70)
    print("PATTERN 6: Evaluation — The Quality Control Inspector")
    print("="*70)

    # The source of truth
    context = "Sarah is a JavaScript developer with 8 years of experience. She worked at Netflix and Spotify."

    # First LLM answers a question
    question = "What programming languages does Sarah know?"
    messages = [
        {"role": "system", "content": f"Answer based ONLY on this context: {context}"},
        {"role": "user", "content": question}
    ]

    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    agent_answer = response.choices[0].message.content

    print(f"Context: {context}")
    print(f"\nQuestion: {question}")
    print(f"Agent's Answer: {agent_answer}")

    # Second LLM evaluates
    eval_prompt = f"""Check if this response is accurate based on the context.

Context: {context}

Question: {question}

Response: {agent_answer}

Did the AI hallucinate or make assumptions not in the context?
Respond with JSON: {{"is_acceptable": true/false, "feedback": "explanation"}}"""

    messages = [{"role": "user", "content": eval_prompt}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    evaluation = response.choices[0].message.content

    print(f"\nEvaluator: {evaluation}")

    print("\n💡 Production agents MUST have evaluation. It's your safety net.")
    print("   If evaluation fails → regenerate with feedback → check again\n")


# ============================================================================
# PATTERN 7: PRODUCTION AGENT CLASS — The Professional Blueprint
# ============================================================================
# Key insight: Combine all patterns into clean, deployable architecture

class ProductionAgent:
    """
    Complete production-ready agent combining:
    - RAG (loads context from files)
    - Tools (can take actions)
    - Tool execution loop (the engine)
    - Clean class structure (maintainable)

    This is the blueprint for real-world AI agents.
    """

    def __init__(self, name="Vivek Tiwari"):
        self.name = name
        self.openai = OpenAI()

        # Load RAG context
        self.context = self._load_context()

        # Define tools
        self.tools = self._define_tools()

        print(f"✅ Production agent initialized for {name}")

    def _load_context(self):
        """Load documents for RAG"""
        try:
            reader = PdfReader("me/linkedin.pdf")
            linkedin = "".join([page.extract_text() or "" for page in reader.pages])
        except:
            linkedin = "No LinkedIn data available"

        try:
            with open("me/summary.txt") as f:
                summary = f.read()
        except:
            summary = "No summary available"

        return {"linkedin": linkedin, "summary": summary}

    def _define_tools(self):
        """Define available tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "record_user_email",
                    "description": "Record when a user wants to be contacted",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string"},
                            "name": {"type": "string"},
                            "notes": {"type": "string"}
                        },
                        "required": ["email"],
                        "additionalProperties": False
                    }
                }
            }
        ]

    def record_user_email(self, email, name="Unknown", notes=""):
        """Tool implementation - in production, save to database, send notification, etc."""
        print(f"  📧 Recording contact: {name} ({email})")
        return {"status": "recorded", "email": email}

    def _execute_tool(self, tool_name, arguments):
        """Execute a tool by name"""
        if tool_name == "record_user_email":
            return self.record_user_email(**arguments)
        return {"error": "Unknown tool"}

    def _system_prompt(self):
        """Create system prompt with RAG context"""
        return f"""You are {self.name}'s professional assistant.

## Background:
{self.context['summary']}

## LinkedIn:
{self.context['linkedin'][:500]}...

Answer questions professionally about {self.name}'s background.
If someone wants to connect, use the record_user_email tool."""

    def chat(self, message, history=[]):
        """
        Main chat function with tool execution loop.
        This is the core of the agent.
        """
        messages = [
            {"role": "system", "content": self._system_prompt()}
        ] + history + [
            {"role": "user", "content": message}
        ]

        # THE TOOL EXECUTION LOOP
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools
            )

            if response.choices[0].finish_reason == "tool_calls":
                # Execute tools
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls

                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    result = self._execute_tool(tool_name, arguments)

                    messages.append(message_obj)
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id
                    })
            else:
                done = True

        return response.choices[0].message.content


def demo_production_agent():
    """See the complete production agent in action"""
    print("\n" + "="*70)
    print("PATTERN 7: Production Agent Class — The Professional Blueprint")
    print("="*70)

    agent = ProductionAgent()

    # Simulate a conversation
    conversation = [
        "What's your background?",
        "I'd like to connect. My email is jane@example.com"
    ]

    history = []
    for question in conversation:
        print(f"\nUser: {question}")
        response = agent.chat(question, history)
        print(f"Agent: {response}")

        # Update history
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})

    print("\n💡 This class structure powers millions of $ in production AI agents.")
    print("   RAG + Tools + Clean Architecture = Production Ready\n")


# ============================================================================
# SUMMARY
# ============================================================================

def print_summary():
    """Print what we learned"""
    summary = """
╔════════════════════════════════════════════════════════════════════╗
║                    THE 7 CORE PATTERNS                             ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  1. BASIC LLM CALLS — The Amnesiac Genius                         ║
║     LLMs are stateless. You must provide all context each time.   ║
║                                                                    ║
║  2. CONVERSATION CHAINING — The Conversation Scribe                ║
║     Keep a transcript. Send it all back. Now the AI "remembers".  ║
║                                                                    ║
║  3. LLM ORCHESTRATION — The Creative Team                          ║
║     Generator → Workers → Judge = Better results, lower cost      ║
║                                                                    ║
║  4. RAG — The Open-Book Exam                                       ║
║     Load docs → Stuff into prompt → LLM answers from context      ║
║     Way better than fine-tuning for most use cases                ║
║                                                                    ║
║  5. TOOL USE — The Digital Handyman ⭐ MOST IMPORTANT              ║
║     LLM calls functions → You execute → Add result → Loop back    ║
║     This is what makes agents actually useful                     ║
║                                                                    ║
║  6. EVALUATION — The Quality Control Inspector                     ║
║     Second LLM checks first LLM's work                            ║
║     Prevents hallucinations. Non-negotiable for production.       ║
║                                                                    ║
║  7. PRODUCTION AGENT CLASS — The Professional Blueprint            ║
║     Combine all patterns into clean, deployable architecture      ║
║     This is how real-world agents are built                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

THE TOOL EXECUTION LOOP (Foundation of all agents):
┌──────────────────────────────────────────────────────┐
│ while not done:                                      │
│     response = llm.create(messages, tools)           │
│                                                      │
│     if llm_wants_tool:                               │
│         result = execute_tool()                      │
│         messages.append(tool_result)                 │
│         # Loop back - LLM will use the result        │
│     else:                                            │
│         done = True                                  │
│         return response                              │
└──────────────────────────────────────────────────────┘

WHAT ABOUT PATTERN 8 (AUTONOMOUS AGENTS)?

That's intentionally NOT in this tutorial. Autonomous agents that make
their own decisions without asking permission are powerful but dangerous.
Get these 7 patterns solid first. Then maybe explore autonomy.

Start simple. Add complexity only when you've proven you need it.

NEXT STEPS:
1. Run this file: python complete_tutorial.py
2. Study the production agents in agents/ folder
3. Customize career_agent.py with YOUR data
4. Deploy it: uv run gradio deploy
5. Ship something real
"""
    print(summary)


# ============================================================================
# MAIN - RUN EVERYTHING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AI AGENTS FOUNDATIONS - COMPLETE TUTORIAL")
    print("="*70)
    print("\nYou're about to see all 7 core patterns in action.")
    print("These patterns power 70% of production AI agents in the wild.\n")

    # Run all demos
    demo_basic_llm()
    demo_conversation_chaining()
    demo_llm_orchestration()
    demo_rag_pattern()
    demo_tool_use()
    demo_evaluation()
    demo_production_agent()

    # Show summary
    print_summary()

    print("="*70)
    print("✅ TUTORIAL COMPLETE")
    print("="*70)
    print("\nNow check out the production agents:")
    print("  • python agents/career_agent.py")
    print("  • python agents/support_agent.py")
    print("  • python agents/research_agent.py")
    print("\nStart building. 🚀\n")
