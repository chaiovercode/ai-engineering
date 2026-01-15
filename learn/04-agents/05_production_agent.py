"""
Production Agent - Putting It All Together

A clean, reusable agent class that combines:
- Tool use
- Conversation memory
- Error handling
- Logging

This is the pattern you'd use in production.
"""

import os
import json
import logging
from datetime import datetime
from typing import Callable
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# =============================================================================
# Production Agent Class
# =============================================================================

class Agent:
    """
    A production-ready AI agent with tools and memory.

    Usage:
        agent = Agent(
            name="MyAssistant",
            system_prompt="You are a helpful assistant.",
            tools=[...]
        )
        response = agent.run("Hello!")
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: list[dict] = None,
        tool_functions: dict[str, Callable] = None,
        model: str = "gpt-4o-mini",
        max_turns: int = 10
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_functions = tool_functions or {}
        self.model = model
        self.max_turns = max_turns

        self.client = OpenAI()
        self.conversation_history = []
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the agent."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                f'[{self.name}] %(levelname)s: %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    def reset(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.logger.info("Conversation reset")

    def run(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        Handles tool calls automatically.
        """
        self.logger.info(f"User: {user_message}")

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build messages with system prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]

        # Agent loop
        for turn in range(self.max_turns):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools if self.tools else None,
                    tool_choice="auto" if self.tools else None
                )
            except Exception as e:
                self.logger.error(f"API error: {e}")
                return f"Sorry, I encountered an error: {e}"

            assistant_message = response.choices[0].message

            # Handle tool calls
            if assistant_message.tool_calls:
                messages.append(assistant_message)

                for tool_call in assistant_message.tool_calls:
                    result = self._execute_tool(tool_call)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            else:
                # No tool calls - we have the final response
                final_response = assistant_message.content

                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })

                self.logger.info(f"Assistant: {final_response[:100]}...")
                return final_response

        return "Sorry, I couldn't complete the task in the allowed steps."

    def _execute_tool(self, tool_call) -> str:
        """Execute a tool call and return the result."""
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        self.logger.info(f"Tool: {func_name}({func_args})")

        if func_name not in self.tool_functions:
            return f"Error: Unknown tool '{func_name}'"

        try:
            result = self.tool_functions[func_name](**func_args)
            return json.dumps(result) if isinstance(result, dict) else str(result)
        except Exception as e:
            self.logger.error(f"Tool error: {e}")
            return f"Error executing {func_name}: {e}"


# =============================================================================
# Example: Customer Support Agent
# =============================================================================

def create_support_agent() -> Agent:
    """Create a customer support agent with tools."""

    # Define tools
    def lookup_order(order_id: str) -> dict:
        """Look up order status."""
        # Simulated database lookup
        orders = {
            "ORD-123": {"status": "shipped", "eta": "2024-01-20"},
            "ORD-456": {"status": "processing", "eta": "2024-01-25"},
        }
        return orders.get(order_id, {"error": "Order not found"})

    def check_inventory(product: str) -> dict:
        """Check product inventory."""
        inventory = {
            "laptop": {"in_stock": True, "quantity": 50},
            "headphones": {"in_stock": True, "quantity": 200},
            "keyboard": {"in_stock": False, "quantity": 0},
        }
        return inventory.get(product.lower(), {"error": "Product not found"})

    tools = [
        {
            "type": "function",
            "function": {
                "name": "lookup_order",
                "description": "Look up the status of an order by order ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "Order ID like ORD-123"}
                    },
                    "required": ["order_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_inventory",
                "description": "Check if a product is in stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product": {"type": "string", "description": "Product name"}
                    },
                    "required": ["product"]
                }
            }
        }
    ]

    return Agent(
        name="SupportAgent",
        system_prompt="""You are a friendly customer support agent.
Help customers with order inquiries and product questions.
Be concise and helpful. If you don't have information, say so.""",
        tools=tools,
        tool_functions={
            "lookup_order": lookup_order,
            "check_inventory": check_inventory
        }
    )


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    agent = create_support_agent()

    print("="*60)
    print("Customer Support Agent Demo")
    print("="*60)

    # Test conversations
    print("\n" + "-"*40)
    print(agent.run("What's the status of order ORD-123?"))

    print("\n" + "-"*40)
    print(agent.run("Do you have keyboards in stock?"))

    print("\n" + "-"*40)
    print(agent.run("What about laptops?"))

    # Show conversation memory
    print("\n" + "-"*40)
    print(agent.run("Can you summarize what we discussed?"))
