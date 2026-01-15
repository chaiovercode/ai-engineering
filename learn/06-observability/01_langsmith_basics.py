"""
LangSmith Basics - Tracing and Observability

This module demonstrates core LangSmith features:
- Automatic tracing of LangChain operations
- Custom trace annotations
- Evaluation and feedback
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LangSmith is automatically enabled when these env vars are set:
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your_key
# LANGCHAIN_PROJECT=your_project_name

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize the model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create a simple chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that explains concepts simply."),
    ("human", "{topic}")
])

chain = prompt | llm | StrOutputParser()


def explain_topic(topic: str) -> str:
    """Explain a topic - this will be automatically traced in LangSmith."""
    return chain.invoke({"topic": f"Explain {topic} in simple terms"})


if __name__ == "__main__":
    # Run this and check your LangSmith dashboard for traces
    result = explain_topic("how neural networks learn")
    print(result)
