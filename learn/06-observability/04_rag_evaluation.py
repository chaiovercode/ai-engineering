"""
RAG Evaluation with RAGAS Metrics

When evaluating RAG systems, you need to measure:
1. Retrieval quality - Did we find the right documents?
2. Generation quality - Is the answer good?

This module explains the key metrics and how to implement them.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# RAGAS METRICS EXPLAINED
# =============================================================================

"""
METRIC 1: FAITHFULNESS (Most Important!)
-----------------------------------------
Question: Is the answer grounded in the context, or did the LLM hallucinate?

How it works:
1. Extract claims/statements from the answer
2. For each claim, check if it's supported by the context
3. Score = supported_claims / total_claims

Example:
    Context: "Python was created by Guido van Rossum in 1991"
    Answer: "Python was created by Guido van Rossum. It's the most popular language."

    Claims:
    1. "Python was created by Guido" → SUPPORTED
    2. "Most popular language" → NOT SUPPORTED (hallucination!)

    Faithfulness = 1/2 = 0.5


METRIC 2: ANSWER RELEVANCE
---------------------------
Question: Does the answer actually address what was asked?

Example:
    Question: "How do I install Python?"
    Bad Answer: "Python is a programming language created in 1991..."
    Good Answer: "To install Python, download it from python.org..."


METRIC 3: CONTEXT PRECISION
----------------------------
Question: Are the retrieved documents actually relevant to the question?

How it works:
1. For each retrieved doc, judge if it's relevant
2. Weight by position (relevant docs at top = better)
3. Higher score = less junk in retrieved results


METRIC 4: CONTEXT RECALL
-------------------------
Question: Did we find ALL the documents needed to answer?

How it works:
1. Identify key facts needed to answer (from ground truth)
2. Check which facts are in retrieved context
3. Score = found_facts / total_needed_facts
"""


# =============================================================================
# IMPLEMENTING FAITHFULNESS
# =============================================================================

def evaluate_faithfulness(context: str, answer: str) -> dict:
    """
    Evaluate if the answer is grounded in the context.
    Returns score (0-1) and list of claims with their verification.
    """

    # Step 1: Extract claims from the answer
    extract_prompt = f"""Extract factual claims from this answer.
Return as a JSON list of strings.

Answer: {answer}

Return format: ["claim 1", "claim 2", ...]"""

    claims_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": extract_prompt}],
        response_format={"type": "json_object"}
    )

    import json
    claims_data = json.loads(claims_response.choices[0].message.content)
    claims = claims_data.get("claims", claims_data.get("list", []))

    if not claims:
        return {"score": 1.0, "claims": [], "message": "No claims to verify"}

    # Step 2: Verify each claim against context
    verify_prompt = f"""For each claim, determine if it's supported by the context.
Return JSON with each claim and whether it's "supported" or "not_supported".

Context:
{context}

Claims to verify:
{json.dumps(claims)}

Return format: {{"verifications": [{{"claim": "...", "verdict": "supported/not_supported"}}]}}"""

    verify_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": verify_prompt}],
        response_format={"type": "json_object"}
    )

    verifications = json.loads(verify_response.choices[0].message.content)
    results = verifications.get("verifications", [])

    # Step 3: Calculate score
    supported = sum(1 for r in results if r.get("verdict") == "supported")
    score = supported / len(results) if results else 1.0

    return {
        "score": score,
        "supported": supported,
        "total": len(results),
        "verifications": results
    }


# =============================================================================
# IMPLEMENTING ANSWER RELEVANCE
# =============================================================================

def evaluate_answer_relevance(question: str, answer: str) -> dict:
    """
    Evaluate if the answer addresses the question.
    """

    prompt = f"""Rate how well this answer addresses the question on a scale of 0-1.
0 = completely off-topic
1 = perfectly addresses the question

Question: {question}
Answer: {answer}

Return JSON: {{"score": 0.0-1.0, "reason": "explanation"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    import json
    return json.loads(response.choices[0].message.content)


# =============================================================================
# RETRIEVAL METRICS
# =============================================================================

def calculate_retrieval_metrics(
    retrieved_docs: list[str],
    relevant_docs: list[str]
) -> dict:
    """
    Calculate classic IR metrics for retrieval.

    Args:
        retrieved_docs: Documents that were retrieved (in order)
        relevant_docs: Documents that SHOULD have been retrieved
    """

    relevant_set = set(relevant_docs)
    retrieved_set = set(retrieved_docs)

    # Precision: What % of retrieved are relevant?
    relevant_retrieved = retrieved_set & relevant_set
    precision = len(relevant_retrieved) / len(retrieved_docs) if retrieved_docs else 0

    # Recall: What % of relevant did we find?
    recall = len(relevant_retrieved) / len(relevant_docs) if relevant_docs else 0

    # Hit@K: Is any relevant doc in top K?
    hit_at_1 = retrieved_docs[0] in relevant_set if retrieved_docs else False
    hit_at_3 = any(d in relevant_set for d in retrieved_docs[:3])
    hit_at_5 = any(d in relevant_set for d in retrieved_docs[:5])

    # MRR: Reciprocal rank of first relevant doc
    mrr = 0
    for i, doc in enumerate(retrieved_docs):
        if doc in relevant_set:
            mrr = 1 / (i + 1)
            break

    return {
        "precision": precision,
        "recall": recall,
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hit_at_5": hit_at_5,
        "mrr": mrr
    }


# =============================================================================
# FULL RAG EVALUATION
# =============================================================================

def evaluate_rag_response(
    question: str,
    context: str,
    answer: str,
    expected_docs: list[str] = None,
    retrieved_docs: list[str] = None
) -> dict:
    """
    Run full RAG evaluation with all metrics.
    """

    results = {
        "question": question,
        "answer_preview": answer[:100] + "..."
    }

    # Generation metrics
    print("Evaluating faithfulness...")
    results["faithfulness"] = evaluate_faithfulness(context, answer)

    print("Evaluating answer relevance...")
    results["answer_relevance"] = evaluate_answer_relevance(question, answer)

    # Retrieval metrics (if ground truth provided)
    if expected_docs and retrieved_docs:
        print("Evaluating retrieval...")
        results["retrieval"] = calculate_retrieval_metrics(retrieved_docs, expected_docs)

    return results


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    # Example RAG scenario
    question = "What year was Python created and by whom?"

    context = """
    Python is a high-level programming language.
    It was created by Guido van Rossum and first released in 1991.
    Python emphasizes code readability with its use of significant indentation.
    """

    # Good answer (grounded in context)
    good_answer = "Python was created by Guido van Rossum and released in 1991."

    # Bad answer (contains hallucination)
    bad_answer = "Python was created by Guido van Rossum in 1991. It's now the world's most popular language with over 10 million developers."

    print("="*60)
    print("Evaluating GOOD answer (grounded)")
    print("="*60)
    good_result = evaluate_faithfulness(context, good_answer)
    print(f"Faithfulness: {good_result['score']:.2f}")
    print(f"Supported: {good_result['supported']}/{good_result['total']}")

    print("\n" + "="*60)
    print("Evaluating BAD answer (hallucination)")
    print("="*60)
    bad_result = evaluate_faithfulness(context, bad_answer)
    print(f"Faithfulness: {bad_result['score']:.2f}")
    print(f"Supported: {bad_result['supported']}/{bad_result['total']}")

    print("\nVerifications:")
    for v in bad_result.get("verifications", []):
        status = "✓" if v["verdict"] == "supported" else "✗"
        print(f"  {status} {v['claim'][:50]}...")

    print("\n" + "="*60)
    print("Retrieval Metrics Example")
    print("="*60)
    metrics = calculate_retrieval_metrics(
        retrieved_docs=["doc1", "doc3", "doc5", "doc2", "doc7"],
        relevant_docs=["doc1", "doc2", "doc4"]
    )
    print(f"Precision: {metrics['precision']:.2f}")
    print(f"Recall: {metrics['recall']:.2f}")
    print(f"MRR: {metrics['mrr']:.2f}")
    print(f"Hit@3: {metrics['hit_at_3']}")
