import sys
import os
import uuid
import re
import time
import threading
from datetime import datetime

from langchain_openai import ChatOpenAI

# Import LangGraph pipeline
from langgraph_pipeline import run_research

# Import database models
from database import SessionLocal
from models import ResearchResult


class ResearchService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini")

    def humanize_content(self, content: str) -> str:
        """Humanize the research content to make it feel more natural and warm"""
        humanize_prompt = """You are a skilled writer who transforms AI-generated text into natural, warm, and engaging writing.

CRITICAL FORMATTING REQUIREMENT - You MUST use markdown headers with the # symbol:
- Start with exactly one # Title (main title with single #)
- Use ## Section Name for 3-5 major sections (double ##)
- Use ### Subsection for any subsections (triple ###)

Example format:
# Main Title Here

Introduction paragraph...

## First Major Section

Content here...

### A Subsection

More content...

## Second Major Section

And so on...

Guidelines for the writing:
- Use conversational language and a warm tone
- Remove stiff, corporate phrasing
- Add natural transitions and human observations
- Keep the core information intact but make it readable
- Vary sentence structure for better flow
- Be conversational but maintain professionalism

Content to humanize:
{content}

Output the humanized content. Remember: You MUST use # for title, ## for sections, ### for subsections. Do NOT use bold (**text**) for headers - only use the # markdown syntax.""".format(content=content)

        response = self.llm.invoke(humanize_prompt)
        return response.content if hasattr(response, 'content') else str(response)

    def highlight_content(self, content: str) -> str:
        """Highlight important text with pastel color markers"""
        highlight_prompt = """You are a content highlighter. Your task is to identify important terms, key concepts, definitions, and critical phrases in the following content and mark them for highlighting.

Guidelines:
- Identify key terms and important concepts (3-5 per paragraph)
- Mark definitions and technical terms
- Highlight statistics and important data points
- Mark critical insights and conclusions
- Use this format: ==TEXT== for text that should be highlighted
- IMPORTANT: Preserve ALL markdown headers exactly as they are (lines starting with #, ##, or ###)
- Do NOT highlight text inside headers - only highlight text in paragraphs

The markers will be converted to pastel color highlights. Be selective - highlight only truly important content (roughly 5-10% of the text).

Content to highlight:
{content}

Output the content with ==TEXT== markers around important passages. Keep all markdown headers (# ## ###) exactly as they appear.""".format(content=content)

        response = self.llm.invoke(highlight_prompt)
        highlighted = response.content if hasattr(response, 'content') else str(response)

        # Convert == markers to HTML spans with pastel colors
        pastel_colors = ['#FFF9C4', '#F8BBD0']
        color_index = 0

        def replace_highlight(match):
            nonlocal color_index
            text = match.group(1)
            color = pastel_colors[color_index % len(pastel_colors)]
            color_index += 1
            return f'<span style="background-color: {color}; color: #1A1A1A; padding: 2px 4px; border-radius: 3px;">{text}</span>'

        highlighted = re.sub(r'==(.*?)==', replace_highlight, highlighted)
        return highlighted

    def _extract_title(self, content: str) -> str:
        """Extract title from first non-empty line of content"""
        lines = content.split('\n')
        for line in lines:
            clean = line.strip().replace('#', '').strip()
            if clean and len(clean) > 0:
                return clean[:200]  # Max 200 chars
        return "Untitled Research"

    def generate_research(self, input_text: str, input_type: str, mode: str, callback):
        """
        Run LangGraph pipeline with callbacks for real-time updates

        callback receives:
        - agent_start(agent_role, message)
        - agent_progress(agent_role, progress, message)
        - agent_complete(agent_role, output)
        - complete(content, research_id)
        """
        start_time = datetime.now()
        try:
            # Agent phases for progress animation
            agent_phases = {
                'Content Strategist': [
                    'Searching for recent trends...',
                    'Analyzing market data...',
                    'Compiling research findings...',
                ],
                'Blog Writer': [
                    'Creating engaging introduction...',
                    'Writing main content...',
                    'Crafting conclusion...',
                ],
                'Fact Checker': [
                    'Identifying claims...',
                    'Verifying statistics...',
                    'Correcting inaccuracies...',
                ],
                'Content Editor': [
                    'Checking grammar...',
                    'Improving flow...',
                    'Optimizing headings...',
                ],
            }

            # Agent order - note: Fact Checker and Content Editor run in PARALLEL
            agent_names = ['Content Strategist', 'Blog Writer', 'Fact Checker', 'Content Editor']

            # Track progress state
            progress_state = {
                'current_agents': set(),
                'completed_agents': set(),
                'running': True,
            }

            def send_progress_for_agent(agent_name, progress, phase_index):
                """Send progress update for an agent"""
                phases = agent_phases.get(agent_name, ['Processing...'])
                callback({
                    'type': 'agent_progress',
                    'agent': agent_name,
                    'progress': progress,
                    'message': phases[min(phase_index, len(phases) - 1)],
                })

            def langgraph_callback(event):
                """Handle events from LangGraph pipeline"""
                event_type = event.get('type')
                agent_name = event.get('agent')

                if event_type == 'agent_start':
                    progress_state['current_agents'].add(agent_name)
                    callback(event)

                elif event_type == 'agent_complete':
                    progress_state['current_agents'].discard(agent_name)
                    progress_state['completed_agents'].add(agent_name)
                    callback({
                        'type': 'agent_progress',
                        'agent': agent_name,
                        'progress': 100,
                        'message': '',
                    })
                    callback(event)

            def run_progress_animation():
                """Animate progress for active agents"""
                agent_progress = {name: 0 for name in agent_names}
                agent_phase = {name: 0 for name in agent_names}

                while progress_state['running']:
                    # Update progress for all active agents
                    for agent_name in list(progress_state['current_agents']):
                        if agent_name in progress_state['completed_agents']:
                            continue

                        current = agent_progress.get(agent_name, 0)
                        if current < 90:
                            agent_progress[agent_name] = min(current + 8, 90)
                            agent_phase[agent_name] = min(agent_phase[agent_name] + 1, 2)
                            send_progress_for_agent(
                                agent_name,
                                agent_progress[agent_name],
                                agent_phase[agent_name]
                            )

                    time.sleep(1.2)

            # Start progress animation thread
            progress_thread = threading.Thread(target=run_progress_animation, daemon=True)
            progress_thread.start()

            # Send initial start events for sequential agents
            callback({
                'type': 'agent_start',
                'agent': 'Content Strategist',
                'message': agent_phases['Content Strategist'][0],
            })
            progress_state['current_agents'].add('Content Strategist')

            # Run LangGraph pipeline
            result = run_research(input_text, mode, langgraph_callback)

            # Stop progress animation
            progress_state['running'] = False
            time.sleep(0.3)

            # Ensure all agents show as complete
            for agent_name in agent_names:
                if agent_name not in progress_state['completed_agents']:
                    callback({
                        'type': 'agent_progress',
                        'agent': agent_name,
                        'progress': 100,
                        'message': '',
                    })
                    callback({
                        'type': 'agent_complete',
                        'agent': agent_name,
                        'output': '',
                    })

            # Post-processing: humanize the output
            callback({
                'type': 'agent_progress',
                'agent': 'Content Editor',
                'progress': 100,
                'message': 'Humanizing output...',
            })
            humanized_content = self.humanize_content(str(result))

            # Post-processing: highlight important content
            callback({
                'type': 'agent_progress',
                'agent': 'Content Editor',
                'progress': 100,
                'message': 'Adding highlights...',
            })
            final_content = self.highlight_content(humanized_content)

            # Save to database
            research_id = str(uuid.uuid4())
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            db = SessionLocal()
            try:
                research = ResearchResult(
                    id=research_id,
                    input=input_text,
                    input_type=input_type,
                    mode=mode,
                    content=final_content,
                    title=self._extract_title(final_content),
                    status='complete',
                    processing_time_ms=processing_time
                )
                db.add(research)
                db.commit()
            finally:
                db.close()

            # Send final result
            callback({
                'type': 'complete',
                'research_id': research_id,
                'content': final_content,
            })

        except Exception as e:
            callback({
                'type': 'error',
                'message': str(e),
            })
