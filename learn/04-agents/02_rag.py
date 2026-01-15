"""
RAG - Retrieval Augmented Generation

Give AI access to your own data without fine-tuning.
This is how you build chatbots that know about YOUR documents.

How it works:
1. User asks a question
2. Search your documents for relevant content
3. Include that content in the prompt
4. AI answers using your data as context
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


# =============================================================================
# STEP 1: Your Knowledge Base
# =============================================================================
# In production, this would be a vector database like Pinecone or Chroma

KNOWLEDGE_BASE = [
    {
        "id": 1,
        "title": "Return Policy",
        "content": "Products can be returned within 30 days of purchase. Items must be unused and in original packaging. Refunds are processed within 5-7 business days."
    },
    {
        "id": 2,
        "title": "Shipping Information",
        "content": "Standard shipping takes 5-7 business days. Express shipping (2-3 days) is available for $15 extra. Free shipping on orders over $50."
    },
    {
        "id": 3,
        "title": "Contact Support",
        "content": "Email support@example.com or call 1-800-123-4567. Support hours are Mon-Fri 9AM-6PM EST. Average response time is 24 hours."
    },
    {
        "id": 4,
        "title": "Product Warranty",
        "content": "All electronics come with a 1-year manufacturer warranty. Extended 2-year warranty available for purchase. Warranty covers defects, not physical damage."
    }
]


# =============================================================================
# STEP 2: Simple Search (Retrieval)
# =============================================================================
# In production, use embeddings and vector similarity search

def search_knowledge_base(query: str, top_k: int = 2) -> list:
    """
    Simple keyword search. In production, use embeddings:
    1. Convert query to embedding vector
    2. Find documents with similar vectors
    3. Return top matches
    """
    query_words = set(query.lower().split())
    scored_docs = []

    for doc in KNOWLEDGE_BASE:
        # Simple scoring: count matching words
        doc_words = set(doc["content"].lower().split())
        doc_words.update(doc["title"].lower().split())
        score = len(query_words & doc_words)
        scored_docs.append((score, doc))

    # Return top matches
    scored_docs.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scored_docs[:top_k] if score > 0]


# =============================================================================
# STEP 3: RAG Query
# =============================================================================

def rag_query(question: str) -> str:
    """Answer a question using RAG."""

    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print('='*60)

    # Step 1: Retrieve relevant documents
    relevant_docs = search_knowledge_base(question)

    print(f"\n📚 Retrieved {len(relevant_docs)} relevant documents:")
    for doc in relevant_docs:
        print(f"   - {doc['title']}")

    # Step 2: Build context from retrieved documents
    context = "\n\n".join([
        f"**{doc['title']}**\n{doc['content']}"
        for doc in relevant_docs
    ])

    # Step 3: Create prompt with context
    system_prompt = """You are a helpful customer support assistant.
Answer questions based ONLY on the provided context.
If the context doesn't contain the answer, say "I don't have information about that."
Be concise and helpful."""

    user_prompt = f"""Context:
{context}

Question: {question}

Answer based on the context above:"""

    # Step 4: Get AI response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    answer = response.choices[0].message.content
    print(f"\n🤖 Answer: {answer}")

    return answer


# =============================================================================
# BONUS: RAG with Sources
# =============================================================================

def rag_with_sources(question: str) -> dict:
    """RAG that also returns source documents."""

    relevant_docs = search_knowledge_base(question)

    context = "\n\n".join([
        f"[Source {i+1}] {doc['title']}: {doc['content']}"
        for i, doc in enumerate(relevant_docs)
    ])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Answer based on the sources. Cite sources like [Source 1]."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [{"title": d["title"], "id": d["id"]} for d in relevant_docs]
    }


if __name__ == "__main__":
    # Test RAG queries
    rag_query("How long do I have to return a product?")
    rag_query("How can I contact customer support?")
    rag_query("What's covered under warranty?")
    rag_query("Do you sell laptops?")  # Not in knowledge base

    print("\n" + "="*60)
    print("RAG with Sources:")
    print("="*60)
    result = rag_with_sources("What are the shipping options?")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
