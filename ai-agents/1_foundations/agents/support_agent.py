"""
CUSTOMER SUPPORT AGENT
======================

A production-ready AI customer support bot with evaluation and quality control.

PATTERNS DEMONSTRATED:
- ✅ RAG - Loads product documentation and FAQs
- ✅ Tool Use - Create tickets, search knowledge base, escalate issues
- ✅ Evaluation - Second LLM checks responses for quality
- ✅ Retry Loop - Regenerates bad responses automatically

USE CASE:
Deploy this as customer support for your product/service. It answers questions,
creates support tickets, and escalates complex issues. Quality control ensures
accurate, helpful responses.

BEFORE RUNNING:
1. Update PRODUCT_DOCS and FAQS below with your product information
2. Set OPENAI_API_KEY in .env
3. (Optional) Add email/ticketing integrations

RUN:
    python agents/support_agent.py

ARCHITECTURE:
    User Question
        ↓
    Agent responds (with RAG context)
        ↓
    Evaluator checks response
        ↓
    If bad → Regenerate with feedback → Evaluate again
        ↓
    If good → Return to user
"""

from dotenv import load_dotenv
from openai import OpenAI
import json
import gradio as gr
from datetime import datetime

load_dotenv(override=True)


# ============================================================================
# KNOWLEDGE BASE - Your product documentation
# ============================================================================

# TODO: Replace with your actual product documentation
PRODUCT_DOCS = """
# SuperWidget Pro - Documentation

## What is SuperWidget Pro?
SuperWidget Pro is a cloud-based productivity tool that helps teams collaborate.

## Features
- Real-time collaboration with up to 50 users
- 100GB cloud storage per user
- Advanced analytics and reporting
- Mobile apps for iOS and Android
- API access for integrations

## Pricing
- Basic: $10/user/month (5 users max)
- Pro: $25/user/month (50 users max)
- Enterprise: Custom pricing (unlimited users)

## Technical Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (minimum 5 Mbps)
- Mobile: iOS 14+ or Android 10+

## Common Issues
- Slow performance: Check your internet connection
- Login issues: Clear cookies and cache
- Sync problems: Force refresh (Ctrl+F5)
"""

FAQS = """
# Frequently Asked Questions

Q: Can I try before buying?
A: Yes! We offer a 14-day free trial. No credit card required.

Q: How do I cancel my subscription?
A: Go to Settings → Billing → Cancel Subscription. You'll have access until the end of your billing period.

Q: Do you offer student discounts?
A: Yes! Students get 50% off with a valid .edu email address.

Q: Is my data secure?
A: Yes. We use AES-256 encryption and are SOC 2 Type II certified.

Q: Can I export my data?
A: Absolutely! Go to Settings → Data Export to download everything.

Q: What payment methods do you accept?
A: Credit card, PayPal, and wire transfer for annual plans.
"""


# ============================================================================
# TOOLS - Support agent capabilities
# ============================================================================

# Simulated ticket database
TICKETS = []
TICKET_ID = 1000


def create_support_ticket(issue: str, priority: str = "medium", user_email: str = ""):
    """
    TOOL: Create a support ticket for complex issues

    Called when:
    - Issue requires human intervention
    - User explicitly requests to create a ticket
    - Problem can't be solved with documentation
    """
    global TICKET_ID
    TICKET_ID += 1

    ticket = {
        "id": TICKET_ID,
        "issue": issue,
        "priority": priority,
        "user_email": user_email,
        "created_at": datetime.now().isoformat(),
        "status": "open"
    }

    TICKETS.append(ticket)
    print(f"🎫 Ticket #{TICKET_ID} created: {issue[:50]}...")

    return {
        "ticket_id": TICKET_ID,
        "message": f"Ticket #{TICKET_ID} created successfully. Our team will respond within 24 hours.",
        "priority": priority
    }


def search_knowledge_base(query: str):
    """
    TOOL: Search product documentation and FAQs

    Called when:
    - User asks a product question
    - Need to find specific information
    - Looking for known solutions
    """
    # Simple keyword search (in production, use vector search)
    query_lower = query.lower()
    results = []

    # Search in docs
    for line in PRODUCT_DOCS.split('\n'):
        if query_lower in line.lower() and line.strip():
            results.append(f"[DOCS] {line.strip()}")

    # Search in FAQs
    for line in FAQS.split('\n'):
        if query_lower in line.lower() and line.strip():
            results.append(f"[FAQ] {line.strip()}")

    if results:
        return {"results": results[:5], "found": len(results)}  # Top 5 results
    else:
        return {"results": [], "found": 0, "message": "No results found"}


def escalate_to_human(reason: str, user_question: str):
    """
    TOOL: Escalate to human support

    Called when:
    - Issue is too complex for AI
    - User requests to speak to a human
    - Sensitive account issues
    """
    print(f"🚨 ESCALATED: {reason}")
    return {
        "status": "escalated",
        "message": "I've connected you with a human support agent. Someone will be with you shortly.",
        "eta_minutes": 5
    }


# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a support ticket for issues that need human attention",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string", "description": "Description of the issue"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level"
                    },
                    "user_email": {"type": "string", "description": "User's email (if provided)"}
                },
                "required": ["issue"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search product documentation and FAQs for relevant information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate to human support for complex or sensitive issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Why this needs human attention"},
                    "user_question": {"type": "string", "description": "The user's original question"}
                },
                "required": ["reason", "user_question"],
                "additionalProperties": False
            }
        }
    }
]


# ============================================================================
# EVALUATOR - Quality control for responses
# ============================================================================

class ResponseEvaluator:
    """
    Uses a second LLM to check if responses are:
    - Accurate (based on documentation)
    - Helpful (actually answers the question)
    - Professional (appropriate tone)
    - Complete (doesn't leave out important info)
    """

    def __init__(self):
        self.openai = OpenAI()

    def evaluate(self, question: str, response: str, context: str):
        """
        Evaluate if a response is acceptable

        Returns:
            dict: {
                "is_acceptable": bool,
                "feedback": str (what's wrong if not acceptable),
                "score": int (1-10)
            }
        """
        evaluation_prompt = f"""You are evaluating a customer support response for quality.

Context (Product Documentation):
{context[:1500]}

User Question: {question}

Agent Response: {response}

Evaluate this response:
1. Is it accurate based on the documentation?
2. Does it actually answer the question?
3. Is the tone professional and helpful?
4. Are there any made-up facts or hallucinations?
5. Would this satisfy the customer?

Respond with JSON:
{{
    "is_acceptable": true or false,
    "feedback": "specific feedback on what's wrong (if not acceptable)",
    "score": 1-10 rating
}}"""

        try:
            eval_response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": evaluation_prompt}],
                response_format={"type": "json_object"}
            )

            result = json.loads(eval_response.choices[0].message.content)
            print(f"📊 Evaluation: {'✅ PASS' if result['is_acceptable'] else '❌ FAIL'} (Score: {result.get('score', 0)}/10)")

            return result

        except Exception as e:
            print(f"⚠️  Evaluation failed: {e}")
            # If evaluation fails, assume acceptable (don't block user)
            return {"is_acceptable": True, "feedback": "Evaluation error", "score": 5}


# ============================================================================
# SUPPORT AGENT - Main agent with evaluation
# ============================================================================

class SupportAgent:
    """
    Customer support agent with built-in quality control

    FEATURES:
    - RAG from product docs and FAQs
    - Tool use for tickets, search, escalation
    - Automatic evaluation of responses
    - Retry loop with feedback
    """

    def __init__(self, company_name="SuperWidget"):
        self.company_name = company_name
        self.openai = OpenAI()
        self.evaluator = ResponseEvaluator()
        self.context = PRODUCT_DOCS + "\n\n" + FAQS
        print(f"✅ {company_name} Support Agent initialized")

    def _system_prompt(self):
        """Define support agent behavior"""
        return f"""You are a helpful customer support agent for {self.company_name}.

Your role:
- Answer customer questions using the product documentation
- Be friendly, professional, and helpful
- Use tools when appropriate (search, create tickets, escalate)
- Always prioritize customer satisfaction

Product Knowledge:
{self.context}

Guidelines:
- Only use information from the documentation above
- If you don't know something, say so and create a ticket
- For account-specific issues, create a ticket or escalate
- Be concise but thorough
- Always maintain a professional, empathetic tone"""

    def _execute_tool(self, tool_name, arguments):
        """Execute support tools"""
        tools_map = {
            "create_support_ticket": create_support_ticket,
            "search_knowledge_base": search_knowledge_base,
            "escalate_to_human": escalate_to_human
        }

        tool_func = tools_map.get(tool_name)
        if tool_func:
            return tool_func(**arguments)
        return {"error": f"Unknown tool: {tool_name}"}

    def _generate_response(self, messages):
        """Generate a response with tool execution loop"""
        done = False
        max_iterations = 5
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
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls

                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    print(f"🔧 {tool_name}({arguments})")
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

    def chat(self, message, history):
        """
        Chat with evaluation loop

        FLOW:
        1. Generate response
        2. Evaluate quality
        3. If bad → Regenerate with feedback → Evaluate again
        4. Repeat up to 3 times
        5. Return best response
        """
        messages = [
            {"role": "system", "content": self._system_prompt()},
            *history,
            {"role": "user", "content": message}
        ]

        max_retries = 3
        best_response = None
        best_score = 0

        for attempt in range(max_retries):
            print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")

            # Generate response
            response = self._generate_response(messages.copy())

            # Evaluate response
            evaluation = self.evaluator.evaluate(message, response, self.context)

            # Track best response
            score = evaluation.get('score', 0)
            if score > best_score:
                best_score = score
                best_response = response

            # If acceptable, return it
            if evaluation['is_acceptable']:
                print(f"✅ Response accepted on attempt {attempt + 1}")
                return response

            # If not acceptable, add feedback and retry
            if attempt < max_retries - 1:
                print(f"❌ Response not acceptable: {evaluation['feedback']}")
                messages.append({
                    "role": "system",
                    "content": f"FEEDBACK: Previous response was not acceptable. {evaluation['feedback']} Please try again with a better response."
                })

        # If we exhausted retries, return the best we got
        print(f"⚠️  Max retries reached. Returning best response (score: {best_score}/10)")
        return best_response or "I apologize, I'm having trouble answering that. Let me create a ticket for our team to help you."

    def launch(self):
        """Launch Gradio interface"""
        interface = gr.ChatInterface(
            fn=self.chat,
            type="messages",
            title=f"{self.company_name} - AI Support",
            description="Ask me anything about our product! I can answer questions, create support tickets, and escalate to human agents.",
            examples=[
                "How much does the Pro plan cost?",
                "I'm having trouble logging in",
                "Do you offer a free trial?",
                "Can I export my data?",
                "I need to speak with a human"
            ],
            theme="soft"
        )

        print(f"\n🚀 Launching {self.company_name} Support Agent...")
        print("💡 Features: RAG + Tools + Evaluation + Auto-retry")
        print("🌐 Local: http://127.0.0.1:7860\n")

        interface.launch()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("CUSTOMER SUPPORT AGENT WITH EVALUATION")
    print("="*60)

    # TODO: Customize with your company name and docs
    agent = SupportAgent(company_name="SuperWidget")

    agent.launch()
