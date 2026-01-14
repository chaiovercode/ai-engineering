import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crewai import Task
from agents import content_strategist, blog_writer, editor, seo_specialist, fact_checker


def get_research_tasks(topic: str, mode: str, on_start, on_progress, on_complete):
    """
    Generate research tasks with callbacks for progress tracking

    Args:
        topic: The topic to research
        mode: 'gen-z' or 'analytical' - determines the tone and style
        on_start: Callback when agent starts
        on_progress: Callback for progress updates
        on_complete: Callback when agent completes
    """

    # Adjust instructions based on mode
    if mode == 'gen-z':
        research_desc = f"""Research the topic: "{topic}"

        Your task is to:
        1. Focus on what's CURRENT in 2026 - we are now in January 2026
        2. Find recent articles, news, and updates from 2025-2026
        3. Identify what's trending RIGHT NOW in 2026, not old stuff from 2023
        4. Look for good sources (but keep it real)
        5. Put together a vibe check outline with what matters TODAY

        IMPORTANT: Avoid outdated information from 2023 or earlier. Focus on recent 2025-2026 developments.
        Find recent, actually useful info that slaps. No cap."""
        research_output = """A research outline that includes:
        - What people are actually talking about
        - Trends that hit different
        - Cool sources worth checking out
        - Facts and stats that matter
        - Takes from people who know their stuff"""

        writing_desc = """Using the research, write something that actually hits.

        IMPORTANT - Use proper markdown formatting:
        - Start with # for the main title
        - Use ## for major sections
        - Use ### for subsections

        Keep it:
        1. Real and relatable from the jump
        2. Organized with clear headings (# ## ###)
        3. Packed with actual facts and insights
        4. Chill but smart (you know the vibe)
        5. Stuff people can actually use

        Make it something people actually want to read."""
        writing_output = """A piece with proper markdown structure:
        - # Main title at the top
        - ## Section headings throughout
        - ### Subsections where needed
        - Clear flow and engaging content"""

        editing_desc = """Polish this piece without losing the vibe.

        Check:
        1. Does it actually flow?
        2. Is the voice consistent?
        3. Grammar and spelling tight?
        4. Sentences hit the way they should?
        5. Facts check out?
        6. Formatting looks clean?

        Keep it real while making it shine."""
        editing_output = """A polished piece that:
        - Flows naturally from start to finish
        - Keeps consistent voice and vibe
        - No grammar or spelling issues
        - Clean formatting
        - All the facts still there
        - Ready to drop"""

        seo_desc = """Quick SEO polish - just the essentials:
        1. Make sure the headline works for search
        2. Add H2/H3 headings if missing
        3. Keep it natural, no keyword stuffing

        Don't overthink it. Light touch only."""
        seo_output = """Same content with:
        - Search-friendly headline
        - Clear heading structure
        - Ready to publish"""

        fact_check_desc_genz = """CRITICAL: You MUST use the duckduckgo_search tool to verify facts.

        For EVERY factual claim (stats, records, dates, quotes):
        1. USE THE SEARCH TOOL to look it up
        2. Compare what the content says vs what you find
        3. If wrong, REPLACE with the correct info from your search
        4. If you can't verify it, REMOVE the claim

        Example: If content says "scored 50 centuries" - SEARCH for the actual number and correct it.

        DO NOT just pass through content. Actually search and verify each claim."""
        fact_check_output_genz = """Fact-checked content where:
        - Every stat was searched and verified
        - Wrong facts were corrected with real data
        - Unverifiable claims were removed"""

    else:  # analytical mode
        research_desc = f"""Conduct comprehensive research on: "{topic}"

        Your task is to:
        1. Focus exclusively on CURRENT 2026 information - we are in January 2026
        2. Identify recent trends, partnerships, announcements, and developments from 2025-2026
        3. Avoid outdated information from 2023 - focus on RECENT 2025-2026 trends instead
        4. Locate latest expert commentary and recent market analysis from 2025-2026
        5. Develop a structured, evidence-based research outline grounded in CURRENT 2026 data

        CRITICAL: It is now 2026. Do NOT cite 2023 information. Focus ONLY on recent 2025-2026 developments.
        Provide current market intelligence and recent company announcements that are relevant today."""
        research_output = """A detailed research outline with:
        - Key concepts and their interrelationships
        - Documented trends and their implications
        - Authoritative sources (with citations)
        - Quantitative and qualitative data
        - Expert perspectives and analysis
        - Organized by theme and significance"""

        writing_desc = """Using the research, write an analytical piece on this topic.

        IMPORTANT - Use proper markdown formatting:
        - Start with # for the main title
        - Use ## for major sections
        - Use ### for subsections

        Requirements:
        1. Establish context and significance in the introduction
        2. Organize with clear markdown headings (# ## ###)
        3. Integrate evidence, data, and quotes with proper attribution
        4. Maintain rigorous, professional tone throughout
        5. Conclude with synthesis and implications

        The piece should be comprehensive and well-structured with proper headings."""
        writing_output = """A complete analytical piece with:
        - # Main title at the top
        - ## Section headings throughout
        - ### Subsections where needed
        - Evidence-based arguments with proper attribution"""

        editing_desc = """Review and refine this analytical piece for excellence.

        Focus on:
        1. Logical flow and argument coherence
        2. Consistency in analysis and perspective
        3. Correctness of grammar, syntax, and terminology
        4. Academic rigor and citation accuracy
        5. Factual accuracy and source verification
        6. Professional formatting and structure

        Elevate the analysis while preserving intellectual rigor."""
        editing_output = """A refined piece that:
        - Flows logically with strong arguments
        - Consistent analytical perspective
        - Polished writing with correct terminology
        - Proper citations and references
        - All facts verified and accurate
        - Ready for publication or distribution"""

        seo_desc = """Light SEO optimization - essentials only:
        1. Ensure headline is search-friendly
        2. Verify proper H2/H3 heading structure
        3. Keep keywords natural

        Preserve analytical quality. Minimal changes."""
        seo_output = """Optimized content with:
        - Search-friendly headline
        - Proper heading hierarchy
        - Ready for publication"""

        fact_check_desc = """CRITICAL: You MUST use the duckduckgo_search tool to verify facts.

        For EVERY factual claim (statistics, records, dates, quotes):
        1. USE THE SEARCH TOOL to look up the claim
        2. Compare what the content states vs search results
        3. If incorrect, REPLACE with accurate data from your search
        4. If unverifiable, REMOVE the claim entirely

        Example: If content says "revenue of $5 billion" - SEARCH and verify the actual figure.

        DO NOT pass through content unchanged. Actively search and verify each factual claim."""
        fact_check_output = """Rigorously fact-checked content where:
        - Every statistic was searched and verified
        - Incorrect data was replaced with accurate information
        - Unverifiable claims were removed
        - All facts now backed by search results"""

    # Set fact-check variables based on mode
    if mode == 'gen-z':
        fact_check_desc_final = fact_check_desc_genz
        fact_check_output_final = fact_check_output_genz
    else:
        fact_check_desc_final = fact_check_desc
        fact_check_output_final = fact_check_output

    # Create tasks with mode-specific descriptions
    research_task = Task(
        description=research_desc,
        expected_output=research_output,
        agent=content_strategist,
        async_execution=False,
    )

    writing_task = Task(
        description=writing_desc,
        expected_output=writing_output,
        agent=blog_writer,
        async_execution=False,
    )

    fact_check_task = Task(
        description=fact_check_desc_final,
        expected_output=fact_check_output_final,
        agent=fact_checker,
        async_execution=False,
    )

    editing_task = Task(
        description=editing_desc,
        expected_output=editing_output,
        agent=editor,
        async_execution=False,
    )

    seo_task = Task(
        description=seo_desc,
        expected_output=seo_output,
        agent=seo_specialist,
        async_execution=False,
    )

    return [research_task, writing_task, fact_check_task, editing_task, seo_task]
