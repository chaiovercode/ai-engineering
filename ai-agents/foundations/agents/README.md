# Production-Ready AI Agents

Three complete, deployable AI agents demonstrating all foundation patterns in real-world applications.

## 🎯 The Three Agents

### 1. Career Agent (`career_agent.py`)
**Personal AI assistant that represents you professionally**

**Patterns:**
- ✅ RAG (loads your LinkedIn/resume)
- ✅ Tool Use (email capture, notifications)
- ✅ Production architecture

**Use Case:**
Deploy on your personal website to answer questions about your background, experience, and skills. Automatically captures leads when visitors want to connect.

**Run:**
```bash
python agents/career_agent.py
```

**Customize:**
1. Change `name="Your Name"` in the code
2. Add your info to `../me/summary.txt`
3. Add your LinkedIn PDF to `../me/linkedin.pdf`
4. Set PUSHOVER credentials for notifications (optional)

---

### 2. Support Agent (`support_agent.py`)
**Customer support bot with quality control**

**Patterns:**
- ✅ RAG (product docs and FAQs)
- ✅ Tool Use (tickets, search, escalation)
- ✅ **Evaluation (second LLM checks quality)**
- ✅ **Retry loop (auto-regenerates bad responses)**

**Use Case:**
Deploy as customer support for your product/service. Answers questions from documentation, creates support tickets, escalates complex issues. Built-in quality control ensures accurate responses.

**Run:**
```bash
python agents/support_agent.py
```

**Customize:**
1. Update `PRODUCT_DOCS` and `FAQS` with your product info
2. Change `company_name="Your Company"`
3. Add real ticketing system integration
4. Integrate real email/notification systems

---

### 3. Research Agent (`research_agent.py`)
**Multi-agent research system**

**Patterns:**
- ✅ **Orchestration (4 specialized agents working together)**
- ✅ **LLM-as-Judge (quality evaluation)**
- ✅ Conversation chaining (multi-step workflow)
- ✅ Tool Use (simulated web search)

**Agent Roles:**
- **Planner**: Breaks topic into research questions
- **Researchers**: Answer each question (parallel capable)
- **Analyst**: Synthesizes all findings into report
- **Judge**: Evaluates research quality

**Use Case:**
Give it a research topic, and it conducts comprehensive research by orchestrating multiple specialized AI agents. Perfect for market research, competitive analysis, or learning new topics.

**Run:**
```bash
python agents/research_agent.py
```

**Customize:**
1. Replace `simulated_web_search()` with real search API (Tavily, SerpAPI)
2. Add more knowledge sources (databases, APIs, documents)
3. Customize report formatting
4. Add citation tracking

---

## 🏗️ Architecture Patterns

### Career Agent Architecture
```
User Question
    ↓
System Prompt (with LinkedIn/Resume context)
    ↓
Tool Execution Loop
    ├─→ record_user_details (if email provided)
    ├─→ record_unknown_question (if can't answer)
    └─→ Final Response
```

### Support Agent Architecture
```
User Question
    ↓
Agent Response (with product docs context)
    ↓
Evaluator LLM checks quality
    ↓
If Bad → Regenerate with feedback → Evaluate again
    ↓
If Good → Return to user

(Retries up to 3 times for quality)
```

### Research Agent Architecture
```
User Topic
    ↓
Planner Agent → Research Questions [Q1, Q2, Q3...]
    ↓
Researcher Agents (parallel) → Answers [A1, A2, A3...]
    ↓
Analyst Agent → Synthesized Report
    ↓
Judge Agent → Quality Evaluation
    ↓
Final Report (with quality score)
```

---

## 📊 Comparison

| Feature | Career Agent | Support Agent | Research Agent |
|---------|-------------|---------------|----------------|
| **Primary Pattern** | RAG + Tools | Evaluation + Tools | Orchestration |
| **Complexity** | Simple | Medium | Advanced |
| **LLMs Used** | 1 | 2 (Agent + Evaluator) | 4+ (Specialized roles) |
| **Tools** | 2 | 3 | 1 (search) |
| **Best For** | Personal branding | Customer service | Research & analysis |
| **Key Learning** | RAG basics | Quality control | Multi-agent systems |

---

## 🚀 Quick Start

### Run Any Agent:
```bash
# From the 1_foundations directory
python agents/career_agent.py
python agents/support_agent.py
python agents/research_agent.py
```

### Deploy Any Agent:
```bash
# Test locally first
python agents/career_agent.py

# Then deploy to HuggingFace Spaces
cd agents
uv run gradio deploy
```

---

## 🎓 Learning Path

**Start with:** `career_agent.py`
- Simplest architecture
- Learn RAG and basic tools
- Get something deployed quickly

**Then try:** `support_agent.py`
- Add evaluation layer
- Understand quality control
- See retry loops in action

**Finally:** `research_agent.py`
- Master orchestration
- Multiple agents cooperating
- Complex workflows

---

## 💡 Customization Ideas

### Career Agent
- Add GitHub integration (show projects)
- Include blog posts/articles
- Add calendar booking
- Integrate with LinkedIn API for real-time updates

### Support Agent
- Connect to real ticketing system (Zendesk, Intercom)
- Add user authentication
- Track conversation metrics
- A/B test responses

### Research Agent
- Add real web search (Tavily, Brave, SerpAPI)
- Integrate with academic databases
- Add citation management
- Export to PDF/Word
- Add visualization generation

---

## 🔧 Production Checklist

Before deploying any agent to production:

- [ ] Update all placeholder content with real data
- [ ] Add authentication if handling sensitive info
- [ ] Set up proper error logging
- [ ] Add rate limiting
- [ ] Configure monitoring/alerting
- [ ] Test with real users
- [ ] Add analytics tracking
- [ ] Set up backup/recovery
- [ ] Review security (no exposed API keys!)
- [ ] Add usage limits/quotas

---

## 📝 Code Quality

All agents follow production best practices:

✅ **Clean architecture**: Separated concerns (tools, agent logic, UI)
✅ **Comprehensive comments**: Explains what and why
✅ **Error handling**: Graceful failures
✅ **Type hints**: Clear function signatures
✅ **Logging**: Debug what's happening
✅ **Configurable**: Easy to customize
✅ **Deployable**: Ready for Gradio → HuggingFace

---

## 🎯 Success Metrics

After studying these agents, you should be able to:

- ✅ Build a RAG-based agent from scratch
- ✅ Implement tool calling for any use case
- ✅ Add evaluation/quality control
- ✅ Orchestrate multiple agents
- ✅ Deploy to production
- ✅ Customize for your specific needs

---

## 🚨 Common Pitfalls

1. **Forgetting context limits**: Keep system prompts under ~2000 tokens
2. **No evaluation**: Always validate responses before showing users
3. **Infinite loops**: Set max iterations in tool execution loops
4. **Exposed secrets**: Never commit API keys
5. **No error handling**: Always have fallbacks
6. **Poor prompts**: Spend time crafting good system prompts
7. **No logging**: You need to debug what's happening

---

## 🔗 Related Files

- `../complete_tutorial.py` - Learn all patterns step-by-step
- `../README.md` - Complete foundations guide
- `../me/` - Your personal data for RAG

---

**These agents are production-ready templates.** Copy them, customize them, deploy them. They demonstrate everything you learned in the tutorial, applied to real-world use cases.

**Now go build something!** 🚀
