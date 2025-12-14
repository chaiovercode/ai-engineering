"""
RESEARCH & SYNTHESIS AGENT
===========================

A production-ready AI research assistant that gathers, analyzes, and synthesizes information.

PATTERNS DEMONSTRATED:
- ✅ Orchestration - Multiple LLMs with different roles (Researcher, Analyst, Synthesizer)
- ✅ LLM-as-Judge - Quality evaluation of research
- ✅ Conversation Chaining - Multi-step research workflow
- ✅ Tool Use - Web search, data gathering (simulated)

USE CASE:
Give this agent a research topic, and it will:
1. Break down the topic into research questions
2. Gather information from multiple sources
3. Analyze and synthesize findings
4. Produce a comprehensive report

BEFORE RUNNING:
1. Set OPENAI_API_KEY in .env
2. (Optional) Add real web search API (Tavily, SerpAPI, etc.)

RUN:
    python agents/research_agent.py

ARCHITECTURE:
    User Topic
        ↓
    Planner Agent → Breaks into research questions
        ↓
    Researcher Agents → Answer each question (parallel)
        ↓
    Analyst Agent → Synthesizes findings
        ↓
    Judge Agent → Evaluates quality
        ↓
    Final Report
"""

from dotenv import load_dotenv
from openai import OpenAI
import json
import gradio as gr
from datetime import datetime
from typing import List, Dict

load_dotenv(override=True)


# ============================================================================
# SIMULATED KNOWLEDGE BASE - Replace with real web search in production
# ============================================================================

# Simulated knowledge base for demonstration
KNOWLEDGE_BASE = {
    "ai": [
        "Large Language Models (LLMs) are neural networks trained on vast amounts of text data",
        "AI agents can use tools to interact with the real world through function calling",
        "RAG (Retrieval Augmented Generation) allows AI to access up-to-date information",
        "The transformer architecture, introduced in 2017, revolutionized NLP"
    ],
    "agents": [
        "AI agents combine LLMs with tools, memory, and planning capabilities",
        "Multi-agent systems have agents with different roles working together",
        "Agent frameworks like LangChain and CrewAI simplify agent development",
        "Evaluation is crucial for production AI agents to prevent hallucinations"
    ],
    "llm": [
        "GPT-4, Claude, and Gemini are leading commercial LLMs in 2024",
        "Open-source models like Llama and Mistral are competitive alternatives",
        "LLMs are stateless and require full context in each API call",
        "Function calling allows LLMs to use external tools and APIs"
    ],
    "programming": [
        "Python is the dominant language for AI development",
        "Gradio and Streamlit make it easy to build AI interfaces",
        "Vector databases enable semantic search for RAG systems",
        "Prompt engineering is crucial for getting good LLM responses"
    ]
}


def simulated_web_search(query: str) -> List[str]:
    """
    Simulated web search - Replace with real API in production

    Real alternatives:
    - Tavily API: https://tavily.com/
    - SerpAPI: https://serpapi.com/
    - Brave Search API: https://brave.com/search/api/
    """
    query_lower = query.lower()
    results = []

    # Simple keyword matching
    for topic, facts in KNOWLEDGE_BASE.items():
        if topic in query_lower:
            results.extend(facts)

    # Also check in individual facts
    for facts_list in KNOWLEDGE_BASE.values():
        for fact in facts_list:
            if any(word in fact.lower() for word in query_lower.split()):
                if fact not in results:
                    results.append(fact)

    return results[:5]  # Return top 5 results


# ============================================================================
# RESEARCH ORCHESTRATION - Multiple agents working together
# ============================================================================

class ResearchOrchestrator:
    """
    Coordinates multiple specialized agents for research

    AGENTS:
    - Planner: Breaks topic into research questions
    - Researcher: Answers individual questions
    - Analyst: Synthesizes all findings
    - Judge: Evaluates quality

    PATTERN: Generator → Workers → Synthesizer → Judge
    """

    def __init__(self):
        self.openai = OpenAI()
        print("✅ Research Orchestrator initialized")

    # ========================================================================
    # AGENT 1: PLANNER - Breaks down research topic
    # ========================================================================

    def plan_research(self, topic: str) -> List[str]:
        """
        Planner Agent: Breaks a research topic into specific questions

        Role: Strategic planner that identifies what needs to be researched
        """
        print(f"\n📋 PLANNER: Breaking down topic '{topic}'...")

        prompt = f"""You are a research planner. Given a topic, break it down into 3-5 specific,
focused research questions that need to be answered.

Topic: {topic}

Respond with JSON:
{{
    "questions": ["question 1", "question 2", ...]
}}"""

        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        questions = result.get('questions', [])

        print(f"✅ Generated {len(questions)} research questions")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")

        return questions

    # ========================================================================
    # AGENT 2: RESEARCHER - Answers individual questions
    # ========================================================================

    def research_question(self, question: str) -> Dict:
        """
        Researcher Agent: Answers a specific research question

        Role: Information gatherer that finds and summarizes answers
        """
        print(f"\n🔍 RESEARCHER: Answering '{question[:60]}...'")

        # Gather information (simulated web search)
        search_results = simulated_web_search(question)

        if not search_results:
            return {
                "question": question,
                "answer": "No relevant information found.",
                "sources": []
            }

        # Synthesize findings
        context = "\n".join([f"- {result}" for result in search_results])

        prompt = f"""You are a researcher. Based on the information below, answer this question concisely.

Question: {question}

Information found:
{context}

Provide a clear, factual answer based only on the information given."""

        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content
        print(f"✅ Answer: {answer[:100]}...")

        return {
            "question": question,
            "answer": answer,
            "sources": search_results
        }

    # ========================================================================
    # AGENT 3: ANALYST - Synthesizes all findings
    # ========================================================================

    def synthesize_research(self, topic: str, research_results: List[Dict]) -> str:
        """
        Analyst Agent: Synthesizes all research into a coherent report

        Role: Strategic thinker that finds patterns and draws conclusions
        """
        print(f"\n📊 ANALYST: Synthesizing {len(research_results)} findings...")

        # Compile all research
        research_summary = ""
        for i, result in enumerate(research_results, 1):
            research_summary += f"\n## Question {i}: {result['question']}\n"
            research_summary += f"Answer: {result['answer']}\n"

        prompt = f"""You are a research analyst. Synthesize the research findings below into a
comprehensive, well-structured report on the topic.

Topic: {topic}

Research Findings:
{research_summary}

Create a report with:
1. Executive Summary
2. Key Findings (organized thematically)
3. Conclusions
4. Recommendations for further research

Use markdown formatting."""

        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        report = response.choices[0].message.content
        print(f"✅ Report generated ({len(report)} chars)")

        return report

    # ========================================================================
    # AGENT 4: JUDGE - Evaluates research quality
    # ========================================================================

    def evaluate_research(self, topic: str, report: str) -> Dict:
        """
        Judge Agent: Evaluates quality of the research report

        Role: Quality control that identifies gaps and areas for improvement
        """
        print(f"\n⚖️  JUDGE: Evaluating research quality...")

        prompt = f"""You are evaluating a research report for quality.

Topic: {topic}

Report:
{report}

Evaluate:
1. Completeness: Does it cover the topic well?
2. Clarity: Is it well-organized and easy to understand?
3. Accuracy: Are claims supported by the research?
4. Usefulness: Would this help someone learn about the topic?

Respond with JSON:
{{
    "overall_score": 1-10,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "is_acceptable": true or false,
    "feedback": "overall assessment"
}}"""

        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        evaluation = json.loads(response.choices[0].message.content)

        score = evaluation.get('overall_score', 0)
        acceptable = evaluation.get('is_acceptable', False)

        print(f"{'✅' if acceptable else '❌'} Score: {score}/10 - {'PASS' if acceptable else 'NEEDS IMPROVEMENT'}")

        return evaluation

    # ========================================================================
    # ORCHESTRATION - Putting it all together
    # ========================================================================

    def conduct_research(self, topic: str) -> Dict:
        """
        Main orchestration method - coordinates all agents

        FLOW:
        1. Planner breaks down topic
        2. Researchers answer each question (could be parallel)
        3. Analyst synthesizes findings
        4. Judge evaluates quality
        5. If poor quality, could retry (not implemented here)
        """
        print("\n" + "="*60)
        print(f"RESEARCH: {topic}")
        print("="*60)

        # Step 1: Plan research questions
        questions = self.plan_research(topic)

        # Step 2: Research each question
        research_results = []
        for question in questions:
            result = self.research_question(question)
            research_results.append(result)

        # Step 3: Synthesize findings
        report = self.synthesize_research(topic, research_results)

        # Step 4: Evaluate quality
        evaluation = self.evaluate_research(topic, report)

        return {
            "topic": topic,
            "questions": questions,
            "research": research_results,
            "report": report,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# RESEARCH AGENT - Gradio interface
# ============================================================================

class ResearchAgent:
    """Web interface for the research orchestrator"""

    def __init__(self):
        self.orchestrator = ResearchOrchestrator()
        print("✅ Research Agent ready")

    def research(self, topic: str, history) -> str:
        """
        Conduct research on a topic and return formatted report
        """
        if not topic or len(topic.strip()) < 5:
            return "Please provide a research topic (at least 5 characters)."

        # Conduct research
        results = self.orchestrator.conduct_research(topic)

        # Format response
        response = f"""# Research Report: {topic}

{results['report']}

---

## Quality Evaluation
**Score:** {results['evaluation'].get('overall_score', 0)}/10
**Status:** {'✅ Acceptable' if results['evaluation'].get('is_acceptable') else '⚠️ Needs Improvement'}

**Strengths:**
{chr(10).join(['- ' + s for s in results['evaluation'].get('strengths', [])])}

**Areas for Improvement:**
{chr(10).join(['- ' + w for w in results['evaluation'].get('weaknesses', [])])}

---

*Research completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Note: This demo uses simulated web search. In production, integrate real search APIs.*
"""

        return response

    def launch(self):
        """Launch Gradio interface"""
        interface = gr.ChatInterface(
            fn=self.research,
            type="messages",
            title="🔬 AI Research Assistant",
            description="**Multi-Agent Research System**\n\nThis agent orchestrates multiple specialized AI agents to conduct comprehensive research:\n- **Planner**: Breaks down topics\n- **Researchers**: Gather information\n- **Analyst**: Synthesizes findings\n- **Judge**: Evaluates quality\n\nTry topics like: 'AI agents', 'Large Language Models', 'RAG systems'",
            examples=[
                "What are AI agents and how do they work?",
                "Explain Large Language Models",
                "How does RAG improve AI responses?",
                "What are the latest developments in LLM engineering?"
            ],
            theme="soft"
        )

        print("\n🚀 Launching Research Agent...")
        print("💡 Pattern: Planner → Researchers → Analyst → Judge")
        print("🌐 Local: http://127.0.0.1:7860\n")

        interface.launch()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("MULTI-AGENT RESEARCH SYSTEM")
    print("="*60)
    print("\nDemonstrates:")
    print("- Orchestration (multiple specialized agents)")
    print("- LLM-as-Judge (quality evaluation)")
    print("- Workflow chaining (plan → research → synthesize → evaluate)")
    print("\n" + "="*60 + "\n")

    agent = ResearchAgent()
    agent.launch()
