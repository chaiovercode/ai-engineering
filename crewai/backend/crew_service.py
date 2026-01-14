import sys
import os

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

# Load tasks module
tasks_spec = importlib.util.spec_from_file_location("tasks", os.path.join(pipeline_path, "tasks.py"))
tasks_module = importlib.util.module_from_spec(tasks_spec)
sys.path.insert(0, pipeline_path)
tasks_spec.loader.exec_module(tasks_module)
get_research_tasks = tasks_module.get_research_tasks

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

    def generate_research(self, input_text: str, input_type: str, mode: str, callback):
        """
        Run CrewAI pipeline with callbacks for real-time updates

        callback receives:
        - agent_start(agent_role, message)
        - agent_progress(agent_role, progress, message)
        - agent_complete(agent_role, output)
        - complete(content)
        """
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

            # Track progress per agent
            agent_progress_state = {}

            def _on_agent_start(agent_role: str) -> None:
                agent_progress_state[agent_role] = {'phase_index': 0, 'progress': 10, 'running': True}

                callback({
                    'type': 'agent_start',
                    'agent': agent_role,
                    'message': agent_phases[agent_role][0],
                })

                # Start periodic progress updates in background thread
                def progress_animation():
                    while agent_progress_state.get(agent_role, {}).get('running', False):
                        time.sleep(1.2)  # Update every 1.2 seconds

                        state = agent_progress_state.get(agent_role, {})
                        if state.get('running', False):
                            phases = agent_phases.get(agent_role, ['Processing...'])
                            phase_index = state.get('phase_index', 0)
                            # Increment progress up to 95% (will reach 100% on completion)
                            progress = min(state.get('progress', 10) + 15, 95)

                            # Send progress update
                            message = phases[min(phase_index, len(phases) - 1)]
                            callback({
                                'type': 'agent_progress',
                                'agent': agent_role,
                                'progress': progress,
                                'message': message,
                            })

                            # Update state
                            agent_progress_state[agent_role]['progress'] = progress
                            agent_progress_state[agent_role]['phase_index'] = min(phase_index + 1, len(phases) - 1)

                thread = threading.Thread(target=progress_animation, daemon=True)
                thread.start()

            def _on_agent_progress(agent_role: str, progress: int, message: str) -> None:
                callback({
                    'type': 'agent_progress',
                    'agent': agent_role,
                    'progress': progress,
                    'message': message,
                })

            def _on_agent_complete(agent_role: str, output: str) -> None:
                # Stop progress updates for this agent
                if agent_role in agent_progress_state:
                    agent_progress_state[agent_role]['running'] = False

                callback({
                    'type': 'agent_progress',
                    'agent': agent_role,
                    'progress': 100,
                    'message': '',  # Empty message, status text will show "complete"
                })

                callback({
                    'type': 'agent_complete',
                    'agent': agent_role,
                    'output': output,
                })

            # Get agents
            agents = [content_strategist, blog_writer, editor, seo_specialist]

            # Get tasks - each task's agent calls the callbacks
            tasks = get_research_tasks(
                input_text,
                mode,
                _on_agent_start,
                _on_agent_progress,
                _on_agent_complete,
            )

            # Pre-start all agents to show initial states
            for i, agent in enumerate(agents):
                _on_agent_start(agent.role)
                # Stagger agent start times for visual flow
                time.sleep(0.3)

            # Create crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=False,
            )

            # Execute crew
            result = crew.kickoff()

            # Mark all agents as complete in sequence
            for i, agent in enumerate(agents):
                _on_agent_complete(agent.role, str(result))
                time.sleep(0.2)

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

            # Send final result
            callback({
                'type': 'complete',
                'content': final_content,
            })

        except Exception as e:
            callback({
                'type': 'error',
                'message': str(e),
            })
