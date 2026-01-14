import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crewai import Agent
from crewai_tools import tool
from langchain_openai import ChatOpenAI
import requests

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Web Search Tool - uses DuckDuckGo for reliable current information
@tool
def web_search(query: str) -> str:
    """
    Search the web for current information about a topic.
    Returns recent search results with sources.
    """
    try:
        # Using DuckDuckGo API via ddg-python-tools or direct SERP search
        # This will fetch current information from the web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Alternative: Use Google Search API or Serper API if SERPER_API_KEY is set
        serper_api_key = os.getenv('SERPER_API_KEY')
        if serper_api_key:
            url = "https://google.serper.dev/search"
            payload = {
                "q": query,
                "num": 10,
                "gl": "us",
                "type": "news"  # Get recent news results
            }
            headers['X-API-KEY'] = serper_api_key

            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('organic', [])

                    # Format results
                    formatted = f"Search results for '{query}':\n\n"
                    for i, result in enumerate(results[:5], 1):
                        formatted += f"{i}. {result.get('title', '')}\n"
                        formatted += f"   URL: {result.get('link', '')}\n"
                        formatted += f"   Snippet: {result.get('snippet', '')}\n\n"
                    return formatted
            except Exception as e:
                pass

        # Fallback: use DuckDuckGo (no API key needed)
        try:
            # Using duck-duckgo-search
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=10, timelimit='w')  # Last week

                formatted = f"Search results for '{query}':\n\n"
                for i, result in enumerate(results[:5], 1):
                    formatted += f"{i}. {result['title']}\n"
                    formatted += f"   URL: {result['href']}\n"
                    formatted += f"   Snippet: {result['body']}\n\n"
                return formatted
        except ImportError:
            # Final fallback
            return f"Recent search results for: {query}\n[Set SERPER_API_KEY for real web search results]"

    except Exception as e:
        return f"Error searching for '{query}': {str(e)}\n[Note: Install 'duckduckgo-search' or set SERPER_API_KEY for web search]"

# Content Strategist Agent
content_strategist = Agent(
    role="Content Strategist",
    goal="Research and identify the latest trends, insights, and sources for the given topic using web search",
    backstory="""You are an expert content strategist with years of experience researching
    and analyzing trends. You excel at finding reliable, current sources and extracting key insights
    that form the foundation for excellent content. You always perform web searches to ensure
    you have the most recent information, avoiding outdated data.""",
    tools=[web_search],
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
