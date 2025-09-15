# RAG Mastery Todo List

## 🔧 Core RAG Concepts

- [ ] **Large Language Models (LLMs) basics** - Understanding response generation, limitations, and hallucinations | 📖 [What is RAG? — AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [ ] **Embedding models and semantic similarity** - How text becomes vectors and why that matters | 📖 [Vector Databases — Weaviate](https://weaviate.io/blog/what-is-a-vector-database)
- [ ] **Vector databases and chunking** - Storage, retrieval, and breaking documents into digestible pieces | 📖 [Understanding Vector Databases — Microsoft](https://learn.microsoft.com/en-us/data-engineering/playbook/solutions/vector-database/)
- [ ] **Basic retrieval pipeline** - The classic retriever → reranker → augmentation → generation flow | 📖 [RAG Tutorial — SingleStore](https://www.singlestore.com/blog/a-guide-to-retrieval-augmented-generation-rag/)

## 🚀 Advanced Retrieval Techniques

- [ ] **Hybrid search** - Combine keyword-based (BM25/sparse) with semantic/dense retrieval | 📖 [Advanced RAG Methods — Premai](https://blog.premai.io/advanced-rag-methods-simple-hybrid-agentic-graph-explained/)
- [ ] **Multi-vector retrieval** - Different embeddings for different content types | 📖 [Advanced RAG Techniques — FalkorDB](https://falkordb.com/blog/advanced-rag/)
- [ ] **Hierarchical retrieval** - Coarse-to-fine search (document → section → chunk) | 📖 [Advanced RAG Methods — Premai](https://blog.premai.io/advanced-rag-methods-simple-hybrid-agentic-graph-explained/)
- [ ] **Advanced reranking** - LLM-based and cross-encoder models for better relevance | 📖 [RAG Techniques — IBM](https://www.ibm.com/think/topics/rag-techniques)

## 🌍 Real-World Data Challenges

- [ ] **Query rewriting and expansion** - Fix ambiguous or poorly-formed user questions | 📖 [Advanced RAG Techniques — TechAhead](https://www.techaheadcorp.com/blog/advanced-rag-techniques-from-pre-retrieval-to-generation/)
- [ ] **Chunk overlap strategies** - Maintain context at boundaries without redundancy | 📖 [Advanced RAG Techniques — FalkorDB](https://falkordb.com/blog/advanced-rag/)
- [ ] **Metadata filtering** - Search by date, document type, source, etc. | 📖 [Understanding Vector Databases — Microsoft](https://learn.microsoft.com/en-us/data-engineering/playbook/solutions/vector-database/)
- [ ] **Source attribution and citations** - Track where information comes from | 📖 [Advanced RAG Techniques — FalkorDB](https://falkordb.com/blog/advanced-rag/)
- [ ] **Context window management** - Handle truncation when you retrieve too much | 📖 [Advanced RAG Techniques — TechAhead](https://www.techaheadcorp.com/blog/advanced-rag-techniques-from-pre-retrieval-to-generation/)

## 📊 Evaluation & Quality Control

- [ ] **RAG evaluation metrics** - Faithfulness, relevance, groundedness, answer quality | 📖 [RAG Tutorial — SingleStore](https://www.singlestore.com/blog/a-guide-to-retrieval-augmented-generation-rag/)
- [ ] **Hallucination detection** - Catch when LLMs make stuff up despite good context | 📖 [Advanced RAG Techniques — TechAhead](https://www.techaheadcorp.com/blog/advanced-rag-techniques-from-pre-retrieval-to-generation/)
- [ ] **Human and automated evaluation** - Build repeatable quality assessment protocols | 📖 [Learn RAGs from Scratch — ProjectPro](https://www.projectpro.io/article/learn-rag-from-scratch/1061)

## 🏭 Production & Scaling

- [ ] **Caching strategies** - Embeddings, queries, responses - cache smart, not hard | 📖 [Advanced RAG Techniques — TechAhead](https://www.techaheadcorp.com/blog/advanced-rag-techniques-from-pre-retrieval-to-generation/)
- [ ] **Incremental data updates** - Add new documents without rebuilding everything | 📖 [Advanced RAG Techniques — FalkorDB](https://falkordb.com/blog/advanced-rag/)
- [ ] **Multi-modal RAG** - Handle text, images, tables, PDFs like a champ | 📖 [Advanced RAG Techniques — FalkorDB](https://falkordb.com/blog/advanced-rag/)
- [ ] **Cost optimization** - API calls, tokens, and compute efficiency matter | 📖 [RAG Tutorial — SingleStore](https://www.singlestore.com/blog/a-guide-to-retrieval-augmented-generation-rag/)
- [ ] **Agentic RAG patterns** - Multi-agent orchestration and reasoning about retrieval | 📖 [Advanced RAG Methods — Premai](https://blog.premai.io/advanced-rag-methods-simple-hybrid-agentic-graph-explained/)

## 🔄 Advanced Systems

- [ ] **Feedback loops** - Active learning and continuous improvement | 📖 [Learn RAGs from Scratch — ProjectPro](https://www.projectpro.io/article/learn-rag-from-scratch/1061)
- [ ] **Adversarial considerations** - Handle crafted queries and poisoned documents | 📖 [Advanced RAG Techniques — TechAhead](https://www.techaheadcorp.com/blog/advanced-rag-techniques-from-pre-retrieval-to-generation/)
- [ ] **Real-time updates** - Keep your knowledge base fresh | 📖 [Advanced RAG Techniques — FalkorDB](https://falkordb.com/blog/advanced-rag/)
- [ ] **Monitoring and observability** - Know when things break before users do | 📖 [Advanced RAG — Microsoft](https://learn.microsoft.com/en-us/azure/developer/ai/advanced-retrieval-augmented-generation)

## 📚 Additional Resources

- [Make Your Own RAG — Hugging Face](https://huggingface.co/blog/ngxson/make-your-own-rag)
- [Learn RAG From Scratch — freeCodeCamp](https://www.youtube.com/watch?v=sVcwVQRHIc8&ab_channel=freeCodeCamp.org)
- [Building Enterprise AI RAG — ByteVagabond](https://bytevagabond.com/post/how-to-build-enterprise-ai-rag/)