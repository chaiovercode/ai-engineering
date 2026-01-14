import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crewai import Agent
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Content Strategist Agent
content_strategist = Agent(
    role="Content Strategist",
    goal="Research and identify key trends, insights, and sources for the given topic",
    backstory="""You are an expert content strategist with years of experience researching
    and analyzing trends. You excel at finding reliable sources and extracting key insights
    that form the foundation for excellent content.""",
    tools=[],
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
