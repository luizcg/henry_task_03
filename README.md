# Multi-Agent Routing System for Acme Corporation

An intelligent query routing system that classifies user questions by department (HR, IT Support, Finance, Legal) and routes them to specialized RAG agents for context-aware answers.

## Features

- **Multi-label Intent Classification**: Queries can be routed to multiple departments simultaneously
- **Specialized RAG Agents**: Each department has its own agent with domain-specific documents
- **Answer Synthesis**: When multiple agents respond, answers are merged into a unified response
- **Full Observability**: Complete workflow tracing with Langfuse
- **Quality Evaluation**: Automated response scoring (bonus feature)
- **Flexible CLI**: Supports CLI arguments, piped stdin, and interactive REPL

## Project Structure

```
henry_task_03/
├── data/                          # Source documents
│   ├── hr_docs/                   # HR policies and procedures
│   ├── tech_docs/                 # IT support documentation
│   ├── finance_docs/              # Finance policies
│   └── legal_docs/                # Legal and compliance docs
├── src/                           # Source code
│   ├── __init__.py
│   ├── config.py                  # Configuration settings
│   ├── indexing.py                # Document indexing script
│   ├── multi_agent_system.py      # Main entrypoint
│   ├── evaluator.py               # Response quality evaluator (bonus)
│   └── agents/
│       ├── __init__.py
│       ├── base_agent.py          # Shared RAG agent utilities
│       ├── hr_agent.py            # HR department agent
│       ├── tech_agent.py          # IT Support agent
│       ├── finance_agent.py       # Finance department agent
│       ├── legal_agent.py         # Legal department agent
│       └── orchestrator.py        # Intent classifier + router
├── faiss_index/                   # Vector stores (created after indexing)
├── traces/                        # Exported Langfuse traces (JSON)
├── test_queries.json              # Test queries with expected intents
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── implementation_decisions.md    # Technical decisions (Q&A format)
└── README.md                      # This file
```

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Package

```bash
# Install in development mode (recommended)
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - LANGFUSE_PUBLIC_KEY (optional, for tracing)
# - LANGFUSE_SECRET_KEY (optional, for tracing)
```

### 4. Index Documents

Before running the system, you must index the documents into vector stores:

```bash
# Index all domains
acme-index

# Or index a specific domain
acme-index --domain hr

# Alternative (without package install)
python -m src.indexing
```

This creates FAISS vector stores in the `faiss_index/` directory.

## Usage

### Interactive REPL (Recommended)

```bash
acme-assistant
```

This starts an interactive session where you can ask questions:

```
🤖 Acme Corporation Support Assistant
========================================
Ask questions about HR, IT, Finance, or Legal.
Type 'exit' or 'quit' to leave.

acme-assistant> How do I request PTO?

📋 Classification: hr
   Reasoning: Question about time off policy

💬 Answer:
To request PTO at Acme Corporation...

📚 Sources:
   - data/hr_docs/01_pto_and_leave_policy.md
```

### Single Question (CLI)

```bash
acme-assistant --question "How do I reset my password?"
acme-assistant -q "What is the expense reimbursement policy?"
```

### Piped Input

```bash
echo "How do I connect to the VPN?" | acme-assistant
cat question.txt | acme-assistant
```

### Verbose Mode

```bash
acme-assistant -v -q "How do I request PTO?"
```

## Architecture

### Intent Classification (Multi-Label)

The orchestrator uses an LLM to classify queries into one or more departments:

- `hr` - Human Resources
- `tech` - IT Support
- `finance` - Finance
- `legal` - Legal
- `other` - Out of scope

A single query can match multiple departments (e.g., "How is unused PTO paid out?" → `["hr", "finance"]`).

### RAG Agents

Each department has a specialized RAG agent with:

- **Separate FAISS index**: Domain-specific documents only
- **Custom system prompt**: Tailored to the department's role
- **Retrieval**: Top-k relevant document chunks

### Answer Synthesis

When multiple agents respond, a synthesizer LLM merges the answers into a coherent, unified response.

### Langfuse Integration

When configured, all workflow steps are traced:

- Intent classification
- Document retrieval per agent
- LLM responses
- Answer synthesis

View traces at [cloud.langfuse.com](https://cloud.langfuse.com).

#### Exported Traces

Langfuse does not support exporting shareable trace URLs, so trace data was exported as JSON files and stored in the `traces/` directory. These files contain the full trace information including spans, LLM calls, and metadata for each query execution.

## Evaluator (Bonus)

The evaluator scores responses on three dimensions (1-10):

- **Relevance**: Does the answer address the question?
- **Completeness**: Is the answer thorough?
- **Accuracy**: Is the information correct?

### Piped Evaluation (Recommended)

Pipe the assistant's JSON output directly to the evaluator:

```bash
acme-assistant -q "How do I request PTO?" --json | acme-evaluate
```

The `--json` flag outputs structured data that the evaluator parses automatically.

### Manual Evaluation

```bash
acme-evaluate \
  --query "How do I request PTO?" \
  --answer "Submit a request in the HR Portal..." \
  --context "PTO requests must be submitted..."
```

## Configuration

Key settings in `src/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_MODEL_NAME` | `gpt-4o-mini` | OpenAI model for LLM calls |
| `EMBEDDING_MODEL_NAME` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | 800 | Characters per document chunk |
| `CHUNK_OVERLAP` | 200 | Overlap between chunks |
| `RETRIEVER_K` | 4 | Documents retrieved per query |

## Testing

Run test queries to validate the system:

```bash
# Test a single query
acme-assistant -q "How do I submit an expense report?"

# Review test_queries.json for more examples
```

## Technical Decisions

See [`implementation_decisions.md`](implementation_decisions.md) for detailed explanations of:

- Why FAISS was chosen as the vector store
- Why separate indexes per domain
- Why LCEL runnables instead of LangGraph
- Why multi-label classification
- RAG configuration choices

For a detailed technical overview with architecture diagrams, see [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md).

---

## 🐛 Troubleshooting

### "FAISS index not found" Error

```
FileNotFoundError: FAISS index not found at faiss_index/hr
```

**Solution**: Run the indexing command first:
```bash
acme-index
# or: python -m src.indexing
```

### "OPENAI_API_KEY not set" Error

**Solution**: Create a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...
```

### Slow First Response

The first query may take 5-10 seconds as models and indexes are loaded into memory. Subsequent queries will be faster.

### "Rate limit exceeded" Error

OpenAI rate limits apply. Solutions:
- Wait a few seconds and retry
- Use a paid OpenAI account for higher limits
- Reduce `RETRIEVER_K` in `config.py` to make fewer embedding calls

### Langfuse Traces Not Appearing

1. Verify `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set in `.env`
2. Check the Langfuse dashboard for your project
3. Traces may take 30-60 seconds to appear

### Out of Memory Errors

FAISS indexes are loaded into RAM. For large document collections:
- Reduce `CHUNK_SIZE` to create smaller chunks
- Use `FAISS.load_local(..., allow_dangerous_deserialization=True)` with caution

---

## 🚧 Known Limitations

| Limitation | Description | Workaround |
|------------|-------------|------------|
| **No conversation memory** | Each query is independent; no context from previous questions | Include context in your question |
| **English only** | Documents and queries should be in English | Translate queries before submitting |
| **No authentication** | Designed for demo/development use | Add auth layer for production |
| **Local vector stores** | FAISS indexes stored locally | Use Pinecone/Qdrant for distributed deployment |
| **Single-user** | No concurrent request handling | Add async/queue for production |
| **No streaming** | Responses return all at once | Implement streaming for better UX |
| **Fixed retrieval count** | Always retrieves k=4 documents | Adjust in config or implement dynamic k |

---

## 🔮 Future Improvements

### Short-term
- [ ] **Streaming responses**: Show answers as they're generated
- [ ] **Conversation memory**: Maintain context across multiple turns
- [ ] **Confidence scores**: Show classifier confidence for each intent
- [ ] **Source highlighting**: Show which parts of docs were used

### Medium-term
- [ ] **Async execution**: Parallel agent invocation for faster multi-domain responses
- [ ] **Caching layer**: Cache frequent queries and embeddings
- [ ] **Feedback loop**: Allow users to rate responses for continuous improvement
- [ ] **Admin dashboard**: Web UI for monitoring and configuration

### Long-term
- [ ] **Multi-language support**: Translate queries and responses
- [ ] **Custom fine-tuning**: Fine-tune models on company-specific terminology
- [ ] **Hybrid search**: Combine vector search with keyword search (BM25)
- [ ] **Agent collaboration**: Allow agents to consult each other for complex queries

---

## 📚 Additional Documentation

- [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md) - Detailed architecture and design
- [`implementation_decisions.md`](implementation_decisions.md) - Technical decisions Q&A
- [`test_queries.json`](test_queries.json) - Test cases with expected intents

---

## License

Internal project for demonstration purposes.
