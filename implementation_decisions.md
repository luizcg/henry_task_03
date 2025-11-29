# Implementation Decisions

This document explains the technical decisions behind the multi-agent routing system, organized by topic in a Q&A format. It serves as a design rationale reference for reviewers and future maintainers.

---

## 1. Vector Store Strategy

**Q: Why did we choose Chroma as the vector store?**

A: Chroma was selected for several reasons:

- **Zero external dependencies**: Runs in-process or as a local persistent store without needing a separate server or Docker container.
- **Native LangChain integration**: First-class support via `langchain-chroma`, making retriever setup straightforward.
- **Persistence**: Supports `persist_directory` so embeddings survive restarts without re-indexing.
- **Good for demos and mid-scale**: Handles hundreds to thousands of documents efficiently, which matches our use case.

Alternatives considered:
- **FAISS**: Excellent performance, but lacks built-in persistence and metadata filtering.
- **Qdrant**: More features, but requires additional setup (Docker or cloud).
- **Pinecone**: Managed cloud service, but adds external dependency and cost.

---

**Q: Why use separate vector store collections per domain instead of one global store with metadata filtering?**

A: We chose **one Chroma collection per agent** (`chroma_db/hr`, `chroma_db/tech`, etc.) for the following reasons:

- **Retrieval precision**: Each agent's retriever only sees its own documents, eliminating any risk of cross-domain contamination.
- **Debuggability**: When tracing in Langfuse, it's immediately clear which domain's documents were retrieved.
- **Simplicity**: No need for metadata filters in queries; the separation is structural.
- **Assignment alignment**: The requirement explicitly mentions "domain-specific document collections," which maps naturally to separate stores.

The alternative (single store + `{"domain": "hr"}` metadata filter) would work but adds complexity and potential for filter bugs.

---

## 2. Orchestration and Routing

**Q: Why use LangChain runnables (LCEL) instead of LangGraph for the orchestrator?**

A: The routing flow is relatively straightforward:

1. Classify intent(s).
2. Fan out to one or more RAG agents.
3. Optionally synthesize answers.

This pattern fits well within LCEL using `RunnableLambda` for the fan-out/fan-in logic. LangGraph would be beneficial for:

- Complex cyclic flows (e.g., retry loops, human-in-the-loop).
- Long-lived conversational state across many turns.
- Visual graph debugging.

Since our flow is essentially linear with conditional branching, LCEL + Python keeps the code simpler, with fewer dependencies and easier debugging.

---

**Q: Why implement multi-label intent classification (routing to multiple agents) instead of single-label?**

A: Real-world queries often span multiple domains. For example:

- *"How is unused PTO paid out in my final paycheck?"* touches both **HR** (PTO policy) and **Finance** (payroll/payout).
- *"What are the data privacy requirements for vendor contracts?"* touches both **Legal** (privacy) and **Legal** (contracts), but could also involve **Finance** (vendor management).

By allowing the classifier to return multiple intents (e.g., `["hr", "finance"]`), the orchestrator can:

- Query both relevant agents.
- Synthesize a more complete answer.
- Avoid forcing the user to ask the same question twice.

This adds modest complexity but significantly improves answer quality for cross-domain questions.

---

**Q: How does the synthesizer work when multiple agents respond?**

A: When the classifier returns multiple intents:

1. The orchestrator invokes each relevant agent in parallel (or sequentially).
2. Each agent returns its answer along with retrieved context snippets.
3. A **synthesizer chain** (another LLM call) receives:
   - The original user query.
   - The per-agent answers and their sources.
4. The synthesizer produces a unified, coherent response that draws from all sources.

This ensures the user gets one well-structured answer, not multiple fragmented responses.

---

## 3. RAG Configuration

**Q: How did we choose the chunk size and overlap for document splitting?**
A: We use `RecursiveCharacterTextSplitter` with:

- **Chunk size**: ~800 characters.
- **Chunk overlap**: ~200 characters.

Rationale:

- Small enough to fit multiple chunks in context for retrieval.
- Large enough to preserve meaningful paragraphs and policy sections.
- Overlap ensures that sentences split at chunk boundaries are still retrievable.

These values are configurable in `src/config.py` and can be tuned based on retrieval quality testing.

---

**Q: How many documents (`k`) do we retrieve per query?**

A: Default is `k=4`. This balances:

- **Relevance**: Top results are most relevant.
- **Context size**: Keeps the prompt within token limits.
- **Diversity**: Enough chunks to cover different aspects of a topic.

For complex queries, we may increase `k` slightly; for simple lookups, fewer may suffice.

---

## 4. LLM Selection

**Q: Which models do we use and why?**

A: We use OpenAI models via `langchain-openai`:

| Component            | Model           | Rationale                                      |
|----------------------|-----------------|------------------------------------------------|
| Intent classifier    | `gpt-4o-mini`   | Fast, cheap, good at structured classification |
| RAG agents           | `gpt-4o-mini`   | Good balance of quality and cost               |
| Synthesizer          | `gpt-4o-mini`   | Merging answers doesn't need largest model     |
| Evaluator (bonus)    | `gpt-4o-mini`   | Scoring is a focused task                      |

For production or higher-stakes use cases, `gpt-4o` or `gpt-4-turbo` could be substituted.

---

## 5. Langfuse Integration

**Q: How do we instrument tracing with Langfuse?**

A: We use the official `langfuse` callback handler for LangChain:

```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler()  # Reads keys from environment
response = chain.invoke(input, config={"callbacks": [handler]})
```

This automatically captures:

- Each LLM call (classifier, agents, synthesizer).
- Retriever calls and returned documents.
- Latencies and token counts.
- Errors and exceptions.

All spans are nested under a single trace per user query, enabling end-to-end debugging.

---

**Q: How does the evaluator report scores to Langfuse?**

A: After generating a response, the evaluator chain:

1. Receives the original query, final answer, and retrieved context.
2. Produces a numeric score (1–10) and a short justification.
3. Uses the Langfuse Python SDK to attach the score to the current trace:

```python
from langfuse import Langfuse

langfuse = Langfuse()
langfuse.score(
    trace_id=current_trace_id,
    name="answer_quality",
    value=score,
    comment=justification
)
```

This enables filtering and analyzing low-quality responses in the Langfuse dashboard.

---

## 6. CLI / stdin / REPL Design

**Q: Why support three input modes (CLI arg, stdin, REPL)?**

A: Different usage scenarios benefit from different modes:

| Mode         | Use Case                                      |
|--------------|-----------------------------------------------|
| `--question` | Scripting, CI/CD tests, quick one-off queries |
| stdin pipe   | Integration with other tools, batch testing   |
| REPL         | Interactive exploration, demos, debugging     |

The implementation checks:

1. If `--question` is provided, run single query.
2. Else if stdin is not a TTY (piped input), read and run.
3. Else start interactive REPL.

---

**Q: Why use `prompt_toolkit` for the REPL?**

A: `prompt_toolkit` provides:

- Command history (arrow keys to navigate previous queries).
- Readline-like editing (Ctrl-A, Ctrl-E, etc.).
- Clean handling of Ctrl-C and Ctrl-D.
- Potential for future enhancements (autocomplete, syntax highlighting).

It's a lightweight addition (`pip install prompt_toolkit`) that significantly improves the interactive experience over plain `input()`.

---

## 7. Project Structure

**Q: Why organize code into `src/` with submodules?**

A: The structure:

```
src/
  config.py
  indexing.py
  multi_agent_system.py
  agents/
    base_agent.py
    hr_agent.py
    tech_agent.py
    finance_agent.py
    legal_agent.py
    orchestrator.py
  evaluator.py
```

Benefits:

- **Separation of concerns**: Each agent is its own module; orchestration is isolated.
- **Testability**: Individual agents can be tested in isolation.
- **Maintainability**: Adding a new department means adding one new agent file and updating the orchestrator.
- **Assignment alignment**: Matches the suggested structure in the requirements.

---

## 8. Future Considerations

**Q: What would we change for a production deployment?**

A: Several enhancements:

- **Async execution**: Use `ainvoke` for parallel agent calls.
- **Caching**: Cache embeddings and frequent queries.
- **Authentication**: Add API key or OAuth for the service.
- **Rate limiting**: Protect against abuse.
- **Monitoring**: Add metrics (latency histograms, error rates) beyond Langfuse traces.
- **Model upgrades**: Evaluate newer models as they become available.
- **User feedback loop**: Capture explicit user ratings to complement automated evaluation.

---

*This document will be updated as implementation progresses and new decisions are made.*
