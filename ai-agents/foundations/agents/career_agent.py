"""
PERSONAL CAREER AGENT
=====================

A production-ready AI agent that represents you professionally on your website.

PATTERNS DEMONSTRATED:
- ✅ RAG (Retrieval Augmented Generation) - Loads your resume/LinkedIn
- ✅ Tool Use - Records user emails, unknown questions
- ✅ Production Architecture - Clean class structure
- ✅ Gradio Deployment - Web interface

USE CASE:
Deploy this on your personal website. It answers questions about your background,
experience, and skills. When visitors want to connect, it captures their email
and sends you a notification.

BEFORE RUNNING:
1. Add your info to ../me/summary.txt
2. Add your LinkedIn PDF to ../me/linkedin.pdf (optional)
3. Set OPENAI_API_KEY in .env
4. Set PUSHOVER_USER and PUSHOVER_TOKEN for notifications (optional)

RUN:
    python agents/career_agent.py

DEPLOY:
    uv run gradio deploy
"""

from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr

# Load environment variables
load_dotenv(override=True)


# ============================================================================
# NOTIFICATION SERVICE - Send alerts when users engage
# ============================================================================

class PushNotifier:
    """Sends push notifications via Pushover when important events occur"""

    def __init__(self):
        self.user = os.getenv("PUSHOVER_USER")
        self.token = os.getenv("PUSHOVER_TOKEN")
        self.enabled = bool(self.user and self.token)

        if self.enabled:
            print("✅ Push notifications enabled")
        else:
            print("⚠️  Push notifications disabled (PUSHOVER_USER/TOKEN not set)")

    def send(self, message):
        """Send a push notification"""
        if not self.enabled:
            print(f"📧 [Would notify]: {message}")
            return

        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={"token": self.token, "user": self.user, "message": message}
            )
            print(f"📱 Notification sent: {message}")
        except Exception as e:
            print(f"❌ Failed to send notification: {e}")


# ============================================================================
# TOOLS - Functions the AI can call
# ============================================================================

# Global notifier instance
notifier = PushNotifier()


def record_user_details(email: str, name: str = "Visitor", notes: str = ""):
    """
    TOOL: Record when a user wants to get in touch

    The AI calls this when:
    - User provides their email
    - User wants to schedule a call
    - User asks to be contacted
    """
    message = f"🎯 New Contact: {name} ({email})\nNotes: {notes}"
    notifier.send(message)
    return {
        "status": "success",
        "message": f"Thanks {name}! I'll be in touch soon at {email}"
    }


def record_unknown_question(question: str):
    """
    TOOL: Record questions the AI couldn't answer

    The AI calls this when:
    - It doesn't know the answer
    - The question is outside the provided context

    Helps you improve your profile data over time
    """
    message = f"❓ Unanswered: {question}"
    notifier.send(message)
    return {"status": "recorded"}


# Tool definitions in OpenAI format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "record_user_details",
            "description": "Use this when a user provides their email and wants to be contacted. ONLY call this after they explicitly give you their email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "The user's email address"},
                    "name": {"type": "string", "description": "User's name (default: 'Visitor')"},
                    "notes": {"type": "string", "description": "Context about why they want to connect"}
                },
                "required": ["email"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": "ALWAYS use this when you don't know the answer to any question",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question you couldn't answer"}
                },
                "required": ["question"],
                "additionalProperties": False
            }
        }
    }
]


# ============================================================================
# CAREER AGENT - The main agent class
# ============================================================================

class CareerAgent:
    """
    A personal AI assistant that represents you professionally.

    ARCHITECTURE:
    1. Load context (RAG) - Your resume, LinkedIn, summary
    2. Define system prompt - How the AI should behave
    3. Tool execution loop - Handle user questions, call tools when needed
    4. Gradio interface - Web UI for deployment
    """

    def __init__(self, name="Your Name"):
        self.name = name
        self.openai = OpenAI()
        self.context = self._load_context()
        print(f"✅ {name}'s Career Agent initialized")

    def _load_context(self):
        """Load your professional context (RAG pattern)"""
        context = {}

        # Load LinkedIn PDF
        try:
            reader = PdfReader("me/linkedin.pdf")
            context['linkedin'] = "".join([
                page.extract_text() or "" for page in reader.pages
            ])
            print(f"✅ Loaded LinkedIn ({len(context['linkedin'])} chars)")
        except Exception as e:
            context['linkedin'] = "LinkedIn profile not available."
            print(f"⚠️  Could not load LinkedIn: {e}")

        # Load summary
        try:
            with open("me/summary.txt", "r") as f:
                context['summary'] = f.read()
            print(f"✅ Loaded summary ({len(context['summary'])} chars)")
        except Exception as e:
            context['summary'] = "Summary not available."
            print(f"⚠️  Could not load summary: {e}")

        return context

    def _system_prompt(self):
        """
        Create the system prompt that defines AI behavior.

        This is where you:
        - Define the AI's role (acting as you)
        - Provide context (RAG)
        - Set behavioral rules (professional, accurate, helpful)
        """
        return f"""You are acting as {self.name}'s professional AI assistant on their website.

Your role:
- Answer questions about {self.name}'s career, background, skills, and experience
- Be professional and engaging, as if talking to a potential employer or client
- If you don't know something, use the record_unknown_question tool
- If a user wants to connect, ask for their email and use the record_user_details tool

Context about {self.name}:

## Summary
{self.context['summary']}

## LinkedIn Profile
{self.context['linkedin'][:2000]}...

Guidelines:
- Only use information from the context above
- Don't make up or assume facts
- Be concise but informative
- Steer engaged visitors toward getting in touch

Remember: You represent {self.name} - be accurate and professional!"""

    def _execute_tool(self, tool_name, arguments):
        """
        Execute a tool by name (dynamic dispatch pattern)

        Instead of a giant if/else, we look up the function by name.
        This makes adding new tools easy - just define the function.
        """
        tools_map = {
            "record_user_details": record_user_details,
            "record_unknown_question": record_unknown_question
        }

        tool_func = tools_map.get(tool_name)
        if tool_func:
            return tool_func(**arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def chat(self, message, history):
        """
        Main chat function - The tool execution loop

        FLOW:
        1. Build messages with system prompt + history + new message
        2. Call LLM with available tools
        3. If LLM wants to call a tool:
           - Execute the tool
           - Add result to messages
           - Loop back to step 2
        4. If LLM has final answer:
           - Return response

        This loop is THE most important pattern in AI agents.
        """
        messages = [
            {"role": "system", "content": self._system_prompt()},
            *history,
            {"role": "user", "content": message}
        ]

        # Tool execution loop
        done = False
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while not done and iteration < max_iterations:
            iteration += 1

            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            finish_reason = response.choices[0].finish_reason

            if finish_reason == "tool_calls":
                # LLM wants to use tools
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    print(f"🔧 Tool called: {tool_name}({arguments})")

                    # Execute the tool
                    result = self._execute_tool(tool_name, arguments)

                    # Add tool call and result to messages
                    messages.append(message_obj)
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id
                    })

            else:
                # LLM has final answer
                done = True

        return response.choices[0].message.content

    def launch(self):
        """Launch the Gradio web interface"""
        interface = gr.ChatInterface(
            fn=self.chat,
            type="messages",
            title=f"{self.name} - AI Career Assistant",
            description=f"Ask me anything about {self.name}'s professional background, experience, and skills!",
            examples=[
                "What's your background?",
                "What technologies do you work with?",
                "Tell me about your experience",
                "What projects have you worked on?",
                "I'd like to connect - can I share my email?"
            ],
            theme="soft"
        )

        print(f"\n🚀 Launching {self.name}'s Career Agent...")
        print("💡 Local: http://127.0.0.1:7860")
        print("🌍 Deploy: uv run gradio deploy\n")

        interface.launch()


# ============================================================================
# MAIN - Run the agent
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("PERSONAL CAREER AGENT")
    print("="*60)

    # TODO: Change this to your name!
    agent = CareerAgent(name="Vivek Tiwari")

    # Launch web interface
    agent.launch()
