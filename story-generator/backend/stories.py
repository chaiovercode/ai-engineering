"""
Story Generator - AI-powered visual story creation for social media.
Uses Gemini for content generation and image creation.
Uses Tavily (primary) or DuckDuckGo (fallback) for real-time research.
"""

import os
import json
import datetime
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize search clients
tavily_client = None
ddgs_available = False

# Try Tavily first (better quality)
if TAVILY_API_KEY:
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        print("✅ Tavily search enabled")
    except ImportError:
        print("⚠️ Tavily not installed")

# Try DuckDuckGo as fallback
if not tavily_client:
    try:
        from duckduckgo_search import DDGS
        ddgs_available = True
        print("✅ DuckDuckGo search enabled (fallback)")
    except ImportError:
        print("⚠️ No search provider available. Install tavily-python or duckduckgo-search")

# Output directory (can be overridden by backend)
OUTPUT_DIR = "generated_stories"


# =============================================================================
# TRENDING TOPICS
# =============================================================================

CATEGORY_QUERIES = {
    "tech": "latest technology news innovations 2024",
    "ai": "artificial intelligence AI breakthroughs news",
    "india": "India news today trending headlines",
    "world": "world news international headlines today",
    "politics": "politics news government elections policy",
    "sports": "major sports news highlights today",
    "movies": "new movies releases entertainment news",
    "business": "business news startups market trends",
    "finance": "finance stock market crypto investment news",
    "science": "science discoveries research breakthroughs"
}


def get_trending_topics(categories) -> list:
    """
    Fetches trending topics for one or more categories using web search.
    Returns 4 topic suggestions based on latest news.

    Args:
        categories: Either a single category string or list of categories.
                   If multiple categories, searches are combined for cross-category topics.
    """
    # Normalize to list
    if isinstance(categories, str):
        categories = [categories]

    categories = [c.lower() for c in categories]
    print(f"📰 Fetching trending topics for: {', '.join(categories)}...")

    all_results = []

    # Search for each category
    for category in categories:
        query = CATEGORY_QUERIES.get(category, f"latest {category} news today")

        # For multiple categories, do a combined search too
        if len(categories) > 1:
            # Reduce results per category when multiple
            results = _search(query, max_results=4)
        else:
            results = _search(query, max_results=8)

        all_results.extend(results)

    # If multiple categories, also search for intersection (e.g., "India movies Bollywood")
    if len(categories) > 1:
        combined_query = " ".join(categories) + " news today trending"
        combined_results = _search(combined_query, max_results=6)
        all_results.extend(combined_results)

    if not all_results:
        print(f"   ⚠️ No search results, using fallback")
        return _get_fallback_topics(categories[0])

    # Combine search results
    content = "\n".join([f"- {r['title']}: {r['content'][:200]}" for r in all_results if r.get('content')])

    if not content:
        return _get_fallback_topics(categories[0])

    # Build category context for prompt
    if len(categories) > 1:
        category_context = f"the intersection of {' and '.join(categories)}"
        example_hint = f"Topics should relate to BOTH/ALL categories. For example, if categories are 'india' and 'movies', suggest Bollywood/Indian cinema topics."
    else:
        category_context = categories[0]
        example_hint = ""

    # Use Gemini to extract trending topic ideas
    prompt = f"""
    Based on these latest news snippets about {category_context}:

    {content}

    Extract exactly 4 interesting, specific topics that would make great visual story content.

    Requirements:
    - Each topic should be specific and newsworthy (not generic)
    - Topics should be suitable for creating educational Instagram stories
    - Include the key angle that makes it interesting
    - Keep each topic concise (5-10 words)
    {example_hint}

    Return as JSON array of strings only. No markdown.

    Example for "tech":
    ["Apple Vision Pro's First Year Impact", "Humanoid Robots in Amazon Warehouses", "Quantum Computing Breaks Encryption Record", "Neuralink's First Human Trial Results"]

    Example for "india + movies":
    ["Pushpa 2's Record-Breaking Box Office", "Shah Rukh Khan's Comeback Year", "South Indian Films Dominating Bollywood", "Indian Cinema at Cannes 2024"]
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "")
        topics = json.loads(text)
        print(f"   ✅ Found {len(topics)} trending topics")
        return topics[:4]
    except Exception as e:
        print(f"   ⚠️ Topic extraction failed: {e}")
        return _get_fallback_topics(categories[0])


def _get_fallback_topics(category: str) -> list:
    """Fallback topics when search fails."""
    fallbacks = {
        "tech": ["Latest iPhone Features", "Electric Vehicle Revolution", "5G Network Expansion", "Smart Home Innovations"],
        "ai": ["ChatGPT's Latest Updates", "AI in Healthcare Diagnosis", "Autonomous Driving Progress", "AI-Generated Art Controversy"],
        "india": ["India's Economic Growth Story", "Digital India Transformation", "Indian Space Program ISRO", "Make in India Success Stories"],
        "world": ["Global Climate Summit Updates", "UN Peace Initiatives", "International Trade Developments", "Global Health Challenges"],
        "politics": ["Election Campaign Updates", "Policy Reform Debates", "Parliamentary Proceedings", "Political Leadership Changes"],
        "sports": ["Champions League Highlights", "NBA Season Updates", "Cricket World Cup Moments", "Tennis Grand Slam News"],
        "movies": ["Upcoming Blockbuster Releases", "Oscar Predictions", "Streaming Wars Update", "Bollywood Box Office Hits"],
        "business": ["Startup Unicorn Stories", "E-commerce Growth Trends", "Remote Work Revolution", "Green Business Initiatives"],
        "finance": ["Stock Market Analysis", "Cryptocurrency Trends", "Investment Strategies", "Personal Finance Tips"],
        "science": ["Mars Exploration Updates", "Climate Change Research", "Medical Breakthroughs", "Ocean Discovery News"]
    }
    return fallbacks.get(category.lower(), ["Trending Topic 1", "Trending Topic 2", "Trending Topic 3", "Trending Topic 4"])


# =============================================================================
# AESTHETIC DEFINITION
# =============================================================================

def define_series_aesthetic(topic: str, user_aesthetic: str = None) -> dict:
    """
    Defines a consistent visual aesthetic for the entire story series.
    Chooses the best style based on topic, or incorporates user preference.
    """
    print(f"🎨 Defining visual aesthetic for '{topic}'...")

    user_style_hint = ""
    if user_aesthetic and user_aesthetic.strip():
        user_style_hint = f"""
        USER PREFERENCE: The user wants a "{user_aesthetic}" style.
        Incorporate this preference while defining the aesthetic details.
        """

    prompt = f"""
    I'm creating a multi-part Instagram/WhatsApp story series about: "{topic}"
    {user_style_hint}

    Define a CONSISTENT visual aesthetic that will be applied to ALL slides.

    CHOOSE THE BEST STYLE FOR THIS SPECIFIC TOPIC:
    - Historical topics → vintage illustrations, old paper textures, sepia tones
    - Science/Space → cinematic realism, deep blacks, glowing elements
    - Nature/Wildlife → photorealistic, natural earth tones, organic textures
    - Technology/AI → cyberpunk neon, sleek gradients, futuristic minimalism
    - Culture/Travel → vibrant photography style, rich saturated colors
    - Food/Lifestyle → warm cozy aesthetic, soft lighting, appetizing colors
    - Spiritual/Religious → sacred golden tones, ethereal lighting, reverent mood
    - Abstract/Philosophy → artistic painted style, dreamy atmospheres
    - Kids/Fun topics → colorful cartoon/illustration style, playful fonts

    Provide:
    1. art_style: The overall artistic style that BEST FITS this topic
    2. color_palette: 3-4 specific colors with hex codes
    3. lighting: Consistent lighting style
    4. typography_style: Font style that matches the aesthetic
    5. texture: Surface/texture quality
    6. background_style: Background treatment

    Return as a JSON object. No markdown, just raw JSON.

    Example for "Black Holes":
    {{
        "art_style": "cinematic space realism with dramatic lighting",
        "color_palette": "void black #0a0a0a, event horizon orange #ff6b00, stellar blue #4cc9f0, deep purple #7209b7",
        "lighting": "dramatic rim lighting with glowing accents against darkness",
        "typography_style": "sleek futuristic sans-serif in white with blue glow",
        "texture": "smooth with particle effects and light streaks",
        "background_style": "deep space black with subtle star field"
    }}

    Example for "Kedarnath Temple":
    {{
        "art_style": "majestic photorealistic with ethereal atmosphere",
        "color_palette": "snow white #f5f5f5, sacred saffron #ff9933, himalayan blue #4a90a4, ancient stone grey #8b8b83",
        "lighting": "divine golden hour light breaking through mountain mist",
        "typography_style": "elegant serif in gold with subtle glow",
        "texture": "weathered stone, misty atmosphere, snow-dusted surfaces",
        "background_style": "towering snow-capped Himalayan peaks with swirling clouds"
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "")
        aesthetic = json.loads(text)
        print(f"✅ Aesthetic: {aesthetic.get('art_style', 'N/A')}")
        return aesthetic
    except Exception as e:
        print(f"⚠️ Aesthetic generation failed: {e}")
        return {
            "art_style": "modern cinematic illustration",
            "color_palette": "vibrant blues, warm oranges, clean whites",
            "lighting": "soft studio lighting with depth",
            "typography_style": "bold white sans-serif with shadow",
            "texture": "smooth polished surfaces",
            "background_style": "soft gradient background"
        }


# =============================================================================
# DEEP RESEARCH
# =============================================================================

def _search_tavily(query: str, max_results: int = 5) -> list:
    """Search using Tavily API."""
    if not tavily_client:
        return []
    try:
        result = tavily_client.search(query=query, search_depth="advanced", max_results=max_results)
        return [{"title": r.get('title', ''), "content": r.get('content', ''), "url": r.get('url', '')}
                for r in result.get('results', [])]
    except Exception as e:
        print(f"   ⚠️ Tavily search failed: {e}")
        return []


def _search_ddgs(query: str, max_results: int = 5) -> list:
    """Search using DuckDuckGo."""
    if not ddgs_available:
        return []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [{"title": r.get('title', ''), "content": r.get('body', ''), "url": r.get('href', '')}
                    for r in results]
    except Exception as e:
        print(f"   ⚠️ DuckDuckGo search failed: {e}")
        return []


def _search(query: str, max_results: int = 5) -> list:
    """Search using available provider (Tavily preferred, DDGS fallback)."""
    if tavily_client:
        return _search_tavily(query, max_results)
    elif ddgs_available:
        return _search_ddgs(query, max_results)
    return []


def _deep_research(topic: str) -> dict:
    """
    Performs deep research on a topic using multiple search queries.
    Returns dict with 'content' (for AI) and 'sources' (for display).
    """
    print(f"   🔬 Deep researching '{topic}'...")

    all_facts = []
    sources = []  # Track unique sources
    current_year = datetime.datetime.now().year

    # Generate multiple search queries for comprehensive research
    search_queries = [
        f"{topic}",
        f"{topic} interesting facts",
        f"{topic} history significance",
        f"{topic} statistics data {current_year}",
        f"{topic} unique features",
    ]

    seen_urls = set()
    for query in search_queries:
        print(f"      → Searching: {query[:50]}...")
        results = _search(query, max_results=3)
        for r in results:
            if r['content'] and len(r['content']) > 50:
                all_facts.append(f"[{r['title']}]: {r['content']}")
                # Track unique sources
                if r['url'] and r['url'] not in seen_urls:
                    seen_urls.add(r['url'])
                    sources.append({
                        "title": r['title'],
                        "url": r['url']
                    })

    # Deduplicate facts and limit
    unique_facts = list(set(all_facts))[:15]

    if unique_facts:
        print(f"   ✅ Gathered {len(unique_facts)} research snippets from {len(sources)} sources")
        return {
            "content": "\n\n".join(unique_facts),
            "sources": sources[:10]  # Limit to top 10 sources
        }
    else:
        print(f"   ⚠️ No research data found, using AI knowledge only")
        return {"content": "", "sources": []}


def research_topic(topic: str, num_slides: int = 5) -> dict:
    """
    Researches a topic deeply and creates fact-rich story slides.
    Uses web search for real data, then Gemini for storytelling.
    Returns dict with 'slides' and 'sources'.
    """
    print(f"🔍 Researching '{topic}' ({num_slides} slides)...")

    # Perform deep research
    research_result = _deep_research(topic)
    research_content = research_result.get("content", "")
    sources = research_result.get("sources", [])

    research_section = ""
    if research_content:
        research_section = f"""
    =====================================================
    VERIFIED RESEARCH DATA - USE THESE FACTS:
    =====================================================
    {research_content}
    =====================================================

    IMPORTANT: Base your slides on the REAL FACTS above.
    Use specific numbers, dates, statistics, and details from the research.
    Do NOT make up facts - only use information from the research data or well-known verified facts.
    """

    prompt = f"""
    You are a researcher and visual storyteller creating an Instagram/WhatsApp story series about: "{topic}"
    {research_section}

    Create exactly {num_slides} story slides that are FACT-RICH and EDUCATIONAL.

    CRITICAL REQUIREMENTS FOR FACTS:
    - Every slide MUST include a specific, verifiable fact
    - Use REAL numbers: dates, measurements, statistics, percentages
    - Include historical facts with actual years/centuries
    - Mention specific names of architects, builders, rulers when relevant
    - Include scientific or geographical data when applicable
    - If discussing issues (like pollution), use real AQI numbers, health statistics

    CONTENT TO INCLUDE:
    - SPECIFIC FACTS: Real numbers, dates, statistics (e.g., "Built in 1632", "Stands at 73 meters", "AQI exceeds 400")
    - HISTORICAL CONTEXT: When was it built/discovered? By whom? Why?
    - SCALE & SIGNIFICANCE: How does it compare? What records does it hold?
    - UNIQUE DETAILS: What specific feature makes it special?
    - HUMAN IMPACT: How does it affect people? What are the real consequences?

    AVOID:
    - Vague statements without specific facts
    - Celebrity visits or political references
    - Generic descriptions that could apply anywhere
    - Made-up statistics

    CRITICAL - NO YEARS IN TITLES:
    - NEVER put years (2023, 2024, 2025, etc.) in slide titles
    - BAD: "2024: A Year of Smog", "2024's Peak Pollution"
    - GOOD: "A City Choking", "Record-Breaking Smog", "The Pollution Crisis"
    - Keep ALL titles timeless and punchy

    SLIDE STRUCTURE:
    - Slide 1: Hook with a striking fact that grabs attention
    - Middle slides: Deep dive with specific facts, history, data
    - Final slide: Impact, significance, or call to awareness

    For each slide provide:
    1. slide_number (1-{num_slides})
    2. title: Short catchy title (max 5 words)
    3. key_fact: ONE specific, verifiable fact with real numbers/dates (15-25 words)
    4. visual_description: DETAILED scene description for image generation (be specific about what to show)
    5. mood: Emotional tone

    Return as JSON array only. No markdown, no explanation.

    Example for "Delhi Air Pollution":
    [
        {{
            "slide_number": 1,
            "title": "Breathing Poison Daily",
            "key_fact": "Delhi's AQI regularly exceeds 400, when WHO safe limit is just 25. That's 16x the safe level.",
            "visual_description": "Aerial view of Delhi skyline completely obscured by thick grey-brown smog, India Gate barely visible, sun appears as dim orange disc",
            "mood": "alarming"
        }},
        {{
            "slide_number": 2,
            "title": "Silent Health Crisis",
            "key_fact": "Air pollution causes 1.67 million deaths annually in India. Delhi residents lose 10 years of life expectancy.",
            "visual_description": "Split image: healthy pink lungs vs blackened damaged lungs, overlaid on hazy Delhi street with people wearing masks",
            "mood": "sobering"
        }}
    ]
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "")
        slides = json.loads(text)
        print(f"✅ Created {len(slides)} slides")
        return {"slides": slides, "sources": sources}
    except Exception as e:
        print(f"❌ Research failed: {e}")
        return None


# =============================================================================
# IMAGE GENERATION
# =============================================================================

def generate_story_image(slide: dict, topic: str, total_slides: int, aesthetic: dict) -> Image.Image:
    """
    Generates a single story image with consistent aesthetic.
    """
    print(f"🖼️  Generating slide {slide['slide_number']}/{total_slides}: {slide['title']}")

    prompt = f"""
    Create a VERTICAL (9:16) story image for Instagram/WhatsApp.

    TOPIC: {topic}
    SLIDE {slide['slide_number']} OF {total_slides}

    VISUAL SCENE:
    {slide['visual_description']}

    ===== SERIES-WIDE VISUAL CONSISTENCY =====
    ALL slides must share these EXACT properties:

    ART STYLE: {aesthetic.get('art_style', 'cinematic illustration')}
    COLOR PALETTE: {aesthetic.get('color_palette', 'vibrant colors')}
    LIGHTING: {aesthetic.get('lighting', 'soft lighting')}
    TEXTURE: {aesthetic.get('texture', 'smooth surfaces')}
    BACKGROUND: {aesthetic.get('background_style', 'gradient')}

    REQUIREMENTS:
    - Use ONLY colors from the palette
    - Maintain EXACT same art style
    - Keep lighting consistent
    - Match background treatment
    ============================================

    TEXT ON IMAGE:
    - TOP: "{slide['title']}" using {aesthetic.get('typography_style', 'bold white sans-serif')}
    - BOTTOM: "{slide['key_fact']}" in smaller readable text, same font family
    - DO NOT add slide numbers or counters

    CRITICAL - ENGLISH ONLY:
    - ALL text on the image MUST be in English
    - Do NOT use any other language (no Japanese, Chinese, Hindi, etc.)
    - Do NOT use any non-Latin script characters
    - Keep all text simple and readable in English
    Make it a professional social media story card.
    """

    try:
        # Try 1: Primary Model (Gemini 3 Pro)
        try:
            response = client.models.generate_content(
                model='gemini-3-pro-image',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                )
            )
        except Exception as e:
            print(f"   ⚠️ Primary model hit limit/error: {e}")
            print(f"   🔄 Switching to fallback model...")
            # Try 2: Fallback Model (Gemini 2.5 Flash)
            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-image', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                )
            )

        if response.candidates and response.candidates[0].content:
             for part in response.candidates[0].content.parts:
                 if part.inline_data:
                     return Image.open(BytesIO(part.inline_data.data))
        
        # Check generated_images format just in case the model returns that 
        if hasattr(response, 'generated_images') and response.generated_images:
             return Image.open(BytesIO(response.generated_images[0].image.image_bytes))

        print(f"   ⚠️ No image generated")
        return None

    except Exception as e:
        print(f"   ❌ Generation failed: {e}")
        return None


# =============================================================================
# CAPTION GENERATION
# =============================================================================

def generate_story_caption(topic: str, slides: list) -> dict:
    """
    Generates an overall caption and hashtags for the entire story series.
    """
    print(f"✍️  Generating caption for '{topic}'...")

    slide_summaries = "\n".join([f"- {s['title']}: {s['key_fact']}" for s in slides])

    prompt = f"""
    I've created a {len(slides)}-part Instagram/WhatsApp story series about: "{topic}"

    Here are the slides:
    {slide_summaries}

    Generate ONE engaging social media caption for the ENTIRE story series (not per slide).

    Requirements:
    - 2-4 sentences, conversational and engaging tone
    - Highlight the most striking fact from the series
    - Create curiosity to swipe through all slides
    - End with a thought-provoking statement or call to action

    Also provide exactly 3 relevant hashtags (without # symbol).

    Return as JSON object only. No markdown.

    Example:
    {{
        "caption": "Did you know Delhi's air is 16x more toxic than WHO limits? Swipe through to see how this invisible killer is affecting millions. The numbers will shock you.",
        "hashtags": ["DelhiPollution", "AirQuality", "HealthAwareness"]
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(text)
        print(f"✅ Caption generated")
        return result
    except Exception as e:
        print(f"⚠️ Caption generation failed: {e}")
        return {
            "caption": f"Swipe through to discover fascinating facts about {topic}.",
            "hashtags": ["DidYouKnow", "Facts", "Learn"]
        }


# =============================================================================
# TEXT-TO-SLIDES (No Research)
# =============================================================================

def create_slides_from_text(text: str, topic: str = "Custom Content", num_slides: int = 5, user_aesthetic: str = None) -> dict:
    """
    Creates story slides from user-provided text (no web research).
    Uses Gemini 3 Pro to extract key facts and generate slide content.
    """
    print(f"\n{'='*50}")
    print(f"📝 TEXT-TO-SLIDES")
    print(f"{'='*50}")
    print(f"Topic: {topic}")
    print(f"Slides: {num_slides}")
    print(f"Text length: {len(text)} chars")
    print(f"{'='*50}\n")

    # Define aesthetic
    aesthetic = define_series_aesthetic(topic, user_aesthetic)

    # Extract facts and create slides using Gemini 3 Pro
    print(f"🔍 Extracting key facts from text...")

    prompt = f"""
    You are an expert content analyst and visual storyteller.

    I have the following text content that I want to turn into a {num_slides}-slide Instagram/WhatsApp story series:

    ===== USER'S TEXT =====
    {text[:8000]}
    =======================

    Your task:
    1. Analyze this text and extract the {num_slides} most important, interesting, or impactful facts/points
    2. Create engaging story slides from these facts
    3. Each slide should be self-contained but flow as a narrative

    REQUIREMENTS:
    - Extract REAL facts from the provided text - do NOT make up information
    - Each fact should be specific with numbers, names, or concrete details when available
    - Create compelling titles (max 5 words, NO years in titles)
    - Write engaging key facts (15-25 words each)
    - Describe visuals that would work well for each slide

    For each slide provide:
    1. slide_number (1-{num_slides})
    2. title: Short catchy title (max 5 words)
    3. key_fact: The main fact/point extracted from the text (15-25 words)
    4. visual_description: DETAILED scene description for image generation
    5. mood: Emotional tone

    Return as JSON array only. No markdown, no explanation.

    Example output format:
    [
        {{
            "slide_number": 1,
            "title": "The Discovery",
            "key_fact": "Scientists found that the phenomenon occurs in 73% of cases, far higher than previously thought.",
            "visual_description": "Scientists in a modern lab examining data on screens, with charts showing rising percentages",
            "mood": "enlightening"
        }}
    ]
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        text_response = response.text.strip().replace("```json", "").replace("```", "")
        slides = json.loads(text_response)
        print(f"✅ Created {len(slides)} slides from text")
    except Exception as e:
        print(f"❌ Slide extraction failed: {e}")
        return None

    # Generate caption
    caption_data = generate_story_caption(topic, slides)

    # Preview
    print(f"\n📋 Story Plan:")
    for slide in slides:
        print(f"   {slide['slide_number']}. {slide['title']}")

    return {
        "topic": topic,
        "aesthetic": aesthetic,
        "slides": slides,
        "sources": [],  # No sources for pasted text
        "caption": caption_data.get("caption", ""),
        "hashtags": caption_data.get("hashtags", [])
    }


# =============================================================================
# PUBLIC API - Two-Phase Generation
# =============================================================================

def research_story_concept(topic: str, num_slides: int = 5, user_aesthetic: str = None) -> dict:
    """
    Phase 1: Research and plan the story without generating images.
    Returns a plan object for user review/editing, including sources.
    """
    print(f"\n{'='*50}")
    print(f"📚 PHASE 1: RESEARCH & PLANNING")
    print(f"{'='*50}")
    print(f"Topic: {topic}")
    print(f"Slides: {num_slides}")
    print(f"{'='*50}\n")

    aesthetic = define_series_aesthetic(topic, user_aesthetic)
    research_result = research_topic(topic, num_slides)

    if not research_result:
        return None

    slides = research_result.get("slides", [])
    sources = research_result.get("sources", [])

    # Generate overall caption and hashtags
    caption_data = generate_story_caption(topic, slides)

    # Preview
    print(f"\n📋 Story Plan:")
    for slide in slides:
        print(f"   {slide['slide_number']}. {slide['title']}")

    if sources:
        print(f"\n📚 Sources ({len(sources)}):")
        for src in sources[:5]:
            print(f"   - {src['title'][:50]}...")

    return {
        "topic": topic,
        "aesthetic": aesthetic,
        "slides": slides,
        "sources": sources,
        "caption": caption_data.get("caption", ""),
        "hashtags": caption_data.get("hashtags", [])
    }


def generate_story_from_plan(plan: dict, output_dir: str = None) -> list:
    """
    Phase 2: Generate images from an approved plan.
    Returns list of saved file paths.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    topic = plan['topic']
    aesthetic = plan['aesthetic']
    slides = plan['slides']

    print(f"\n{'='*50}")
    print(f"🎨 PHASE 2: IMAGE GENERATION")
    print(f"{'='*50}")
    print(f"Topic: {topic}")
    print(f"Style: {aesthetic.get('art_style', 'Unknown')}")
    print(f"{'='*50}\n")

    os.makedirs(output_dir, exist_ok=True)

    generated_images = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)[:30].strip()

    for slide in slides:
        image = generate_story_image(slide, topic, len(slides), aesthetic)

        if image:
            filename = os.path.join(output_dir, f"{safe_topic}_{timestamp}_slide{slide['slide_number']}.png")
            image.save(filename)
            generated_images.append(filename)
            print(f"   ✅ Saved: {os.path.basename(filename)}")
        else:
            print(f"   ⚠️ Skipped slide {slide['slide_number']}")

        print(f"\n✨ Generated {len(generated_images)}/{len(slides)} images")
    return generated_images


# =============================================================================
# TRENDING TOPICS
# =============================================================================

def get_trending_topics(category: str) -> list:
    """
    Fetches trending topics for a given category using Tavily.
    """
    print(f"🔍 Finding trending topics for '{category}'...")
    
    try:
        query = f"trending {category} topics news headlines today"
        search_result = tavily_client.search(query=query, search_depth="basic", max_results=7)
        
        # Extract potential topics from titles
        topics = []
        for res in search_result.get('results', []):
            title = res.get('title', '')
            # Simple cleanup to make it look like a topic
            if title and len(title) < 80:
                topics.append(title)
        
        if not topics:
            return []
            
        print(f"✅ Found {len(topics)} trending topics")
        return topics[:5] # Return top 5
        
    except Exception as e:
        print(f"⚠️ Trending search failed: {e}")
        return []


# =============================================================================
# PUBLIC API - Single-Call Generation (Backward Compatible)
# =============================================================================

def create_story_series(topic: str, num_slides: int = 5, user_aesthetic: str = None, output_dir: str = None) -> list:
    """
    Complete story generation in one call.
    Combines research and generation phases.
    """
    plan = research_story_concept(topic, num_slides, user_aesthetic)
    if not plan:
        return []
    return generate_story_from_plan(plan, output_dir or OUTPUT_DIR)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n🎬 AI Story Generator")
    print("Create Instagram/WhatsApp stories on any topic!\n")

    topic = input("Enter topic: ").strip() or "The secret life of octopuses"
    num_input = input("Slides (1-10, default 5): ").strip()
    num_slides = int(num_input) if num_input.isdigit() and 1 <= int(num_input) <= 10 else 5
    aesthetic = input("Style (optional): ").strip() or None

    images = create_story_series(topic, num_slides, aesthetic)

    if images:
        print(f"\n📁 Files saved to: {OUTPUT_DIR}/")
        Image.open(images[0]).show()
