import sys
import os
import uuid
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Import from existing pipeline - handle directory name starting with number
import importlib.util
pipeline_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '2_content_pipeline')

# Load agents module
agents_spec = importlib.util.spec_from_file_location("agents", os.path.join(pipeline_path, "agents.py"))
agents_module = importlib.util.module_from_spec(agents_spec)
agents_spec.loader.exec_module(agents_module)
content_strategist = agents_module.content_strategist
blog_writer = agents_module.blog_writer
editor = agents_module.editor
seo_specialist = agents_module.seo_specialist
fact_checker = agents_module.fact_checker

# Load tasks module
tasks_spec = importlib.util.spec_from_file_location("tasks", os.path.join(pipeline_path, "tasks.py"))
tasks_module = importlib.util.module_from_spec(tasks_spec)
sys.path.insert(0, pipeline_path)
tasks_spec.loader.exec_module(tasks_module)
get_research_tasks = tasks_module.get_research_tasks

# Import database models
from database import SessionLocal
from models import ResearchResult


class CrewService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini")

    def humanize_content(self, content: str) -> str:
        """Humanize the research content to make it feel more natural and warm"""
        humanize_prompt = """You are a skilled writer who transforms AI-generated text into natural, warm, and engaging writing. Your task is to take the following research content and make it feel more human, authentic, and personable.

Guidelines:
- Use conversational language and a warm tone
- Remove stiff, corporate phrasing
- Add natural transitions and human observations
- Keep the core information intact but make it more readable and relatable
- Vary sentence structure for better flow
- Be conversational but maintain professionalism
- Remove excessive formality or repetition

Content to humanize:
{content}

Output the humanized version of the content without any markdown code blocks or extra markers.""".format(content=content)

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

The markers will be converted to pastel color highlights. Be selective - highlight only truly important content (roughly 5-10% of the text).

Content to highlight:
{content}

Output the content with ==TEXT== markers around important passages that should be highlighted.""".format(content=content)

        response = self.llm.invoke(highlight_prompt)
        highlighted = response.content if hasattr(response, 'content') else str(response)

        # Convert == markers to HTML spans with pastel colors
        pastel_colors = ['#FFF9C4', '#F8BBD0', '#C8E6C9', '#BBDEFB', '#E1BEE7']
        color_index = 0

        def replace_highlight(match):
            nonlocal color_index
            text = match.group(1)
            color = pastel_colors[color_index % len(pastel_colors)]
            color_index += 1
            return f'<span style="background-color: {color}; padding: 2px 4px; border-radius: 3px;">{text}</span>'

        highlighted = __import__('re').sub(r'==(.*?)==', replace_highlight, highlighted)
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
        Run CrewAI pipeline with callbacks for real-time updates

        callback receives:
        - agent_start(agent_role, message)
        - agent_progress(agent_role, progress, message)
        - agent_complete(agent_role, output)
        - complete(content, research_id)
        """
        start_time = datetime.now()
        try:
            import time
            import threading

            # Agent phases and messages
            agent_phases = {
                'Content Strategist': [
                    'Searching for recent trends and sources...',
                    'Analyzing market data and insights...',
                    'Compiling research findings...',
                    'Building comprehensive outline...',
                ],
                'Blog Writer': [
                    'Creating engaging introduction...',
                    'Writing main content sections...',
                    'Adding examples and case studies...',
                    'Crafting compelling conclusion...',
                ],
                'Fact Checker': [
                    'Identifying factual claims...',
                    'Verifying statistics and data...',
                    'Cross-referencing sources...',
                    'Correcting inaccuracies...',
                ],
                'Content Editor': [
                    'Checking grammar and spelling...',
                    'Improving sentence flow...',
                    'Ensuring consistent tone...',
                    'Final polish and refinement...',
                ],
                'SEO Specialist': [
                    'Analyzing keyword opportunities...',
                    'Optimizing headings and structure...',
                    'Adding meta descriptions...',
                    'Ensuring readability standards...',
                ],
            }

            # Agent order for sequential progress
            agent_names = ['Content Strategist', 'Blog Writer', 'Fact Checker', 'Content Editor', 'SEO Specialist']

            # Track state for sequential progress
            progress_controller = {
                'current_agent_index': 0,
                'running': True,
                'completed': False
            }

            def run_sequential_progress():
                """Run progress animation sequentially - one agent at a time"""
                while progress_controller['running'] and not progress_controller['completed']:
                    current_idx = progress_controller['current_agent_index']
                    if current_idx >= len(agent_names):
                        break

                    agent_name = agent_names[current_idx]
                    phases = agent_phases.get(agent_name, ['Processing...'])

                    # Send agent start
                    callback({
                        'type': 'agent_start',
                        'agent': agent_name,
                        'message': phases[0],
                    })

                    # Animate progress from 0 to 95 for this agent
                    progress = 5
                    phase_index = 0
                    while progress < 95 and progress_controller['running'] and not progress_controller['completed']:
                        # Check if we should still be on this agent
                        if progress_controller['current_agent_index'] != current_idx:
                            break

                        time.sleep(1.5)  # Update every 1.5 seconds

                        if progress_controller['current_agent_index'] != current_idx:
                            break

                        progress = min(progress + 12, 95)
                        phase_index = min(phase_index + 1, len(phases) - 1)

                        callback({
                            'type': 'agent_progress',
                            'agent': agent_name,
                            'progress': progress,
                            'message': phases[phase_index],
                        })

                    # If still on this agent, wait for completion signal or timeout
                    wait_count = 0
                    while (progress_controller['current_agent_index'] == current_idx and
                           progress_controller['running'] and
                           not progress_controller['completed'] and
                           wait_count < 40):  # Max 60 seconds per agent
                        time.sleep(1.5)
                        wait_count += 1

                    # Mark agent complete if we're moving to next
                    if progress_controller['current_agent_index'] > current_idx or progress_controller['completed']:
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

            def advance_to_next_agent():
                """Move to the next agent in sequence"""
                progress_controller['current_agent_index'] += 1

            # Get agents
            agents = [content_strategist, blog_writer, fact_checker, editor, seo_specialist]

            # Get tasks (callbacks not used directly by tasks anymore)
            tasks = get_research_tasks(
                input_text,
                mode,
                lambda x: None,  # Not used
                lambda x, y, z: None,  # Not used
                lambda x, y: None,  # Not used
            )

            # Start progress animation in background
            progress_thread = threading.Thread(target=run_sequential_progress, daemon=True)
            progress_thread.start()

            # Create crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=False,
            )

            # Execute crew (this blocks until all tasks complete)
            # Advance agents based on estimated timing
            def advance_agents_periodically():
                """Advance agents at intervals to simulate real progress"""
                # Estimate ~15-20 seconds per agent for a total of ~75-100 seconds
                for i in range(len(agent_names) - 1):
                    time.sleep(18)  # Wait before advancing to next agent
                    if not progress_controller['completed']:
                        advance_to_next_agent()

            advance_thread = threading.Thread(target=advance_agents_periodically, daemon=True)
            advance_thread.start()

            result = crew.kickoff()

            # Mark as completed
            progress_controller['completed'] = True
            progress_controller['running'] = False

            # Ensure all agents show as complete
            time.sleep(0.5)
            for agent_name in agent_names:
                callback({
                    'type': 'agent_progress',
                    'agent': agent_name,
                    'progress': 100,
                    'message': '',
                })
                callback({
                    'type': 'agent_complete',
                    'agent': agent_name,
                    'output': str(result),
                })
                time.sleep(0.1)

            # Send status update that we're humanizing the output
            callback({
                'type': 'agent_progress',
                'agent': 'SEO Specialist',
                'progress': 100,
                'message': 'Humanizing output for natural feel...',
            })

            # Humanize the final output to make it feel more natural
            humanized_content = self.humanize_content(str(result))

            # Send status update that we're highlighting important content
            callback({
                'type': 'agent_progress',
                'agent': 'SEO Specialist',
                'progress': 100,
                'message': 'Highlighting important content with pastel colors...',
            })

            # Highlight important content with pastel colors
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

            # Send final result with research ID
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
