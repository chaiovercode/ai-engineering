import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crewai import Agent
from langchain_openai import ChatOpenAI
from crewai.tools import tool
from duckduckgo_search import DDGS

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# DuckDuckGo search tool using CrewAI 1.8.0 tool decorator
@tool
def duckduckgo_search(query: str) -> str:
    """Search DuckDuckGo for current, recent information about any topic. Returns latest news and information."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if results:
                output = f"Recent search results for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    output += f"{i}. {result.get('title', 'Untitled')}\n"
                    output += f"   {result.get('body', '')[:300]}\n"
                    output += f"   Source: {result.get('href', '')}\n\n"
                return output
            return f"No recent results found for '{query}'"
    except Exception as e:
        return f"Could not search for '{query}': {str(e)}"

# Content Strategist Agent
content_strategist = Agent(
    role="Content Strategist",
    goal="Research and identify the LATEST 2026 trends, insights, and sources for the given topic",
    backstory="""You are an expert content strategist in January 2026 with knowledge of current events.
    CRITICAL: It is now 2026. You MUST provide information about what is current in 2026, not 2023.
    Focus ONLY on recent developments, trends, and announcements from 2025-2026.
    Completely ignore or deprioritize any information from 2023 or earlier years.
    Reference recent news, partnerships, financial reports, and market shifts from late 2025 and early 2026.
    Synthesize current market intelligence and recent company announcements into your research.""",
    tools=[duckduckgo_search],
    llm=llm,
    verbose=False,
)

# Blog Writer Agent
blog_writer = Agent(
    role="Blog Writer",
    goal="Write engaging, well-structured blog content based on the research",
    backstory="""You are a talented blog writer who excels at crafting engaging,
    informative content that resonates with readers. You have a knack for explaining
    complex topics in an accessible way.""",
    tools=[],
    llm=llm,
    verbose=False,
)

# Content Editor Agent
editor = Agent(
    role="Content Editor",
    goal="Edit and refine the blog content for clarity, flow, and consistency",
    backstory="""You are a meticulous editor with an eye for detail. You improve
    content clarity, fix grammatical issues, and ensure consistent tone and style
    throughout the piece.""",
    tools=[],
    llm=llm,
    verbose=False,
)

# SEO Specialist Agent
seo_specialist = Agent(
    role="SEO Specialist",
    goal="Optimize the content for search engines while maintaining readability",
    backstory="""You are an SEO expert who understands search engine optimization
    without compromising content quality. You know how to incorporate keywords naturally
    and structure content for better rankings.""",
    tools=[],
    llm=llm,
    verbose=False,
)
