import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crewai import Task
from agents import content_strategist, blog_writer, editor, seo_specialist


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

        Keep it:
        1. Real and relatable from the jump
        2. Organized but not boring
        3. Packed with actual facts and insights
        4. Chill but smart (you know the vibe)
        5. Stuff people can actually use
        6. Ending that makes sense

        Make it something people actually want to read."""
        writing_output = """A piece that:
        - Opens strong and keeps it real
        - Has clear sections that flow
        - Uses facts and quotes naturally
        - Keeps it conversational but smart
        - Has actionable takeaways
        - Lands the ending"""

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

        seo_desc = """Make this optimized for search but keep it real.

        Work on:
        1. Keywords that feel natural
        2. Headlines that slap AND work for search
        3. Proper heading structure
        4. Keep it readable (no keyword stuffing)
        5. Help search engines understand it
        6. Internal links where they make sense

        Don't sacrifice the vibe for SEO."""
        seo_output = """A piece that:
        - Has a headline that pops and ranks
        - Good heading structure throughout
        - Keywords fit naturally
        - Still reads smooth
        - Search engines can understand it
        - Ready to share"""

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

        Requirements:
        1. Establish context and significance in the introduction
        2. Organize arguments into logical sections with clear hierarchy
        3. Integrate evidence, data, and quotes with proper attribution
        4. Maintain rigorous, professional tone throughout
        5. Provide analysis and interpretation of findings
        6. Conclude with synthesis and implications

        The piece should be comprehensive, well-researched, and intellectually rigorous."""
        writing_output = """A complete analytical piece with:
        - Contextual introduction
        - Logically structured sections
        - Evidence-based arguments
        - Proper attribution of sources
        - Deep analysis and interpretation
        - Conclusion with broader implications"""

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

        seo_desc = """Optimize this analytical piece for discoverability.

        Focus on:
        1. Strategic keyword integration
        2. SEO-effective headline optimization
        3. Proper heading hierarchy (H2, H3, etc.)
        4. Metadata considerations
        5. Search engine readability
        6. Strategic internal and external linking

        Maintain analytical integrity while improving search visibility."""
        seo_output = """An optimized piece that:
        - Has an SEO-optimized, compelling headline
        - Strategic heading structure
        - Natural keyword integration
        - Maintains analytical rigor
        - Clear structure for search engines
        - Strategic linking included
        - Ready for publication"""

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

    return [research_task, writing_task, editing_task, seo_task]
