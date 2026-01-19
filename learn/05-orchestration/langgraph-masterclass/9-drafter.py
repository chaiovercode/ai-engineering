import sys
from typing import TypedDict, Annotated, Sequence, Literal
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()

# --- 1. State Management ---
# We use a simple class to simulate a database or file system for the draft.
# This prevents using global variables directly and keeps data organized.
class DraftStore:
    def __init__(self):
        self.content = ""

    def update(self, new_content: str) -> str:
        """Updates the internal draft content."""
        self.content = new_content
        return f"Draft updated successfully.\n\nCurrent Content:\n{self.content}"

    def save(self, filename: str) -> str:
        """Saves the internal draft content to a file."""
        # Ensure correct extension
        name = filename if filename.endswith(".txt") else f"{filename}.txt"
        try:
            with open(name, "w") as f:
                f.write(self.content)
            return f"Successfully saved draft to file: {name}"
        except Exception as e:
            return f"Error saving file: {str(e)}"

    def get_content(self) -> str:
        return self.content if self.content else "(Draft is currently empty)"

# Initialize our store instance
store = DraftStore()

# --- 2. Tools ---
# These tools allow the agent to interact with our DraftStore.

@tool
def update_draft(content: str) -> str:
    """Replace the entire document draft with new content. Call this when the user asks to write or edit text."""
    return store.update(content)

@tool
def save_to_file(filename: str, content: str = "") -> str:
    """Save the current draft to a local text file. 
    If 'content' is provided (not empty), it UPDATES the draft before saving.
    """
    if content:
        store.update(content)
    return store.save(filename)

tools = [update_draft, save_to_file]

# --- 3. Agent Setup ---

# We define the state of our graph.
class AgentState(TypedDict):
    # 'messages' tracks the conversation history. 
    # 'add_messages' reducer ensures new messages are appended to the history.
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Create the model and bind our tools to it
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

def agent_node(state: AgentState):
    """The main node that generates a response."""
    
    # 1. Get the current draft content to give the agent context
    current_content = store.get_content()
    
    # 2. Create a system message with instructions and the current state
    system_message = SystemMessage(content=(
        "You are an expert Drafting Assistant.\n"
        "Your goal is to help the user write, edit, and save text documents.\n\n"
        "You have access to the following tools:\n"
        "- `update_draft`: Use this to write or modify the text. You must provide the FULL new content.\n"
        "- `save_to_file`: Use this to save. You can optionally provide 'content' to update and save in one step.\n\n"
        f"CURRENT DRAFT CONTENT:\n{current_content}"
    ))
    
    # 3. Combine system message with the conversation history
    messages = [system_message] + state["messages"]
    
    # 4. Invoke the model
    response = model.invoke(messages)
    
    # 5. Return the response (LangGraph will append it to state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    """Decides the next step: execute tools or end the turn."""
    last_message = state["messages"][-1]
    
    # If the LLM made a tool call, go to the 'tools' node
    if last_message.tool_calls:
        return "tools"
    
    # Otherwise, stop and wait for user input
    return END

# --- 4. Graph Construction ---
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")

# Conditional edge: After 'agent', check if we need to call tools
graph.add_conditional_edges("agent", should_continue)

# Automatic edge: After 'tools', always go back to 'agent' to report the result
graph.add_edge("tools", "agent")

app = graph.compile()

# --- 5. Execution Loop ---
def main():
    print("--- Drafter Agent Started ---")
    print("Type 'quit', 'q', or 'exit' to stop.")
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["q", "quit", "exit"]:
                print("Goodbye!")
                break
            
            # Prepare the input for the agent
            inputs = {"messages": [HumanMessage(content=user_input)]}
            
            # Run the agent and stream the results
            # 'stream_mode="updates"' gives us just the new state changes
            for update in app.stream(inputs, stream_mode="updates"):
                for node_name, node_output in update.items():
                    # Check the messages produced by this node
                    if "messages" in node_output:
                        last_msg = node_output["messages"][-1]
                        
                        # If it's the agent speaking (and not a tool call request)
                        if isinstance(last_msg, BaseMessage) and last_msg.content:
                             print(f"Agent: {last_msg.content}")
                        
                        # (Optional) We could log tool executions here if we wanted
                        # if last_msg.tool_calls:
                        #     print(f"   [Running tool: {last_msg.tool_calls[0]['name']}]")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
