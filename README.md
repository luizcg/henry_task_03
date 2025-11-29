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
├── test_queries.json              # Test queries with expected intents
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── ENUNCIADO.md                   # Original assignment
├── ENUNCIADO.extended.md          # Extended design notes
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

See `implementation_decisions.md` for detailed explanations of:

- Why Chroma was chosen as the vector store
- Why separate collections per domain
- Why LCEL runnables instead of LangGraph
- Why multi-label classification
- RAG configuration choices

## Known Limitations

1. **No conversation memory**: Each query is independent
2. **English only**: Documents and queries should be in English
3. **No authentication**: Designed for demo/development use
4. **Local vector stores**: Not suitable for distributed deployment without changes

## License

Internal project for demonstration purposes.
