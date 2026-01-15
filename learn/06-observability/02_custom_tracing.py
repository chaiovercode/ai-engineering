"""
Custom Tracing with LangSmith

Demonstrates:
- @traceable decorator for custom functions
- Adding metadata and tags to traces
- Nested traces and run trees
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langsmith import traceable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


@traceable(name="research_step")
def research_topic(topic: str) -> str:
    """Research a topic - creates a traced span."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research assistant. Provide key facts about the topic."),
        ("human", "Research: {topic}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"topic": topic})


@traceable(name="summarize_step")
def summarize_research(research: str) -> str:
    """Summarize research findings - creates another traced span."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the following research in 2-3 bullet points."),
        ("human", "{research}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"research": research})


@traceable(
    name="full_research_pipeline",
    metadata={"version": "1.0", "type": "research"},
    tags=["research", "pipeline"]
)
def research_pipeline(topic: str) -> dict:
    """
    Full research pipeline - parent trace containing nested child traces.

    Check LangSmith to see the hierarchical trace structure:
    - full_research_pipeline (parent)
      - research_step (child)
      - summarize_step (child)
    """
    research = research_topic(topic)
    summary = summarize_research(research)

    return {
        "topic": topic,
        "research": research,
        "summary": summary
    }


if __name__ == "__main__":
    result = research_pipeline("quantum computing applications")
    print("=== Research Results ===")
    print(f"\nTopic: {result['topic']}")
    print(f"\nResearch:\n{result['research']}")
    print(f"\nSummary:\n{result['summary']}")
