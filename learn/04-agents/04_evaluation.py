"""
AI Evaluation - Quality Control for LLM Outputs

You can't improve what you can't measure. This module shows
how to evaluate AI outputs programmatically.

Key patterns:
1. LLM-as-Judge: Use another AI to evaluate outputs
2. Criteria-based scoring
3. Comparing outputs
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# Pattern 1: LLM as Judge
# =============================================================================

def evaluate_response(question: str, response: str, criteria: list[str]) -> dict:
    """
    Use an LLM to evaluate another LLM's response.
    This is the foundation of most AI evaluation systems.
    """

    criteria_text = "\n".join([f"- {c}" for c in criteria])

    eval_prompt = f"""Evaluate this AI response on the following criteria.
For each criterion, score 1-5 (1=poor, 5=excellent) and explain why.

Question: {question}

Response: {response}

Criteria to evaluate:
{criteria_text}

Return your evaluation as JSON:
{{
    "scores": {{"criterion_name": score, ...}},
    "explanations": {{"criterion_name": "explanation", ...}},
    "overall_score": average_score,
    "summary": "brief overall assessment"
}}"""

    eval_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": eval_prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(eval_response.choices[0].message.content)


# =============================================================================
# Pattern 2: A/B Testing Responses
# =============================================================================

def compare_responses(question: str, response_a: str, response_b: str) -> dict:
    """
    Compare two responses and pick the better one.
    Useful for comparing different prompts or models.
    """

    compare_prompt = f"""Compare these two AI responses to the same question.
Determine which is better and explain why.

Question: {question}

Response A:
{response_a}

Response B:
{response_b}

Return JSON:
{{
    "winner": "A" or "B",
    "confidence": "high/medium/low",
    "reasons": ["reason1", "reason2"],
    "a_strengths": ["..."],
    "b_strengths": ["..."]
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": compare_prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


# =============================================================================
# Pattern 3: Factual Accuracy Check
# =============================================================================

def check_factual_accuracy(claim: str, context: str = None) -> dict:
    """
    Verify if a claim is factually accurate.
    Optionally provide context/source material.
    """

    prompt = f"""Evaluate the factual accuracy of this claim.

Claim: {claim}
{f"Context/Source: {context}" if context else ""}

Return JSON:
{{
    "verdict": "accurate" | "inaccurate" | "partially_accurate" | "unverifiable",
    "confidence": "high" | "medium" | "low",
    "explanation": "why you reached this verdict",
    "corrections": "corrected version if inaccurate, null otherwise"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


# =============================================================================
# Pattern 4: Automated Test Suite
# =============================================================================

def run_eval_suite(agent_function, test_cases: list[dict]) -> dict:
    """
    Run a suite of test cases against an agent.
    Each test case has: question, expected_criteria
    """

    results = []

    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}/{len(test_cases)}: {test['question'][:50]}...")

        # Get agent response
        response = agent_function(test["question"])

        # Evaluate
        evaluation = evaluate_response(
            test["question"],
            response,
            test.get("criteria", ["accuracy", "helpfulness", "clarity"])
        )

        results.append({
            "question": test["question"],
            "response": response,
            "evaluation": evaluation,
            "passed": evaluation["overall_score"] >= test.get("min_score", 3)
        })

    # Summary
    passed = sum(1 for r in results if r["passed"])
    avg_score = sum(r["evaluation"]["overall_score"] for r in results) / len(results)

    return {
        "total_tests": len(test_cases),
        "passed": passed,
        "failed": len(test_cases) - passed,
        "average_score": round(avg_score, 2),
        "results": results
    }


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo 1: Evaluate a single response
    print("="*60)
    print("Pattern 1: LLM as Judge")
    print("="*60)

    question = "Explain what an API is to a beginner"
    response = """An API is like a waiter at a restaurant. You (the customer)
    don't go directly into the kitchen. Instead, you tell the waiter what you
    want, and they bring it to you. APIs work the same way - they let programs
    talk to each other without knowing how each other works internally."""

    eval_result = evaluate_response(
        question,
        response,
        ["accuracy", "clarity", "appropriate_for_beginners", "use_of_analogies"]
    )

    print(f"Overall Score: {eval_result['overall_score']}/5")
    print(f"Summary: {eval_result['summary']}")

    # Demo 2: Compare responses
    print("\n" + "="*60)
    print("Pattern 2: Compare Responses")
    print("="*60)

    response_a = "An API is an Application Programming Interface that enables communication between software systems."
    response_b = "Think of an API like a universal translator. It lets different programs speak to each other, even if they're written in different languages or by different companies."

    comparison = compare_responses(question, response_a, response_b)
    print(f"Winner: Response {comparison['winner']}")
    print(f"Reasons: {comparison['reasons']}")

    # Demo 3: Fact check
    print("\n" + "="*60)
    print("Pattern 3: Factual Accuracy")
    print("="*60)

    claim = "Python was created in 1995 by James Gosling"
    fact_check = check_factual_accuracy(claim)
    print(f"Verdict: {fact_check['verdict']}")
    print(f"Explanation: {fact_check['explanation']}")
    if fact_check.get('corrections'):
        print(f"Correction: {fact_check['corrections']}")
