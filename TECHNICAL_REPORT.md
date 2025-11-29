# Technical Report: Multi-Agent Routing System

## Executive Summary

This document provides a detailed technical overview of the Multi-Agent Routing System built for Acme Corporation. The system uses LangChain to orchestrate multiple specialized RAG (Retrieval-Augmented Generation) agents that handle employee queries across four departments: HR, IT Support, Finance, and Legal.

**Key Achievements:**
- Multi-label intent classification for cross-domain queries
- Domain-specific RAG agents with isolated knowledge bases
- Full workflow observability via Langfuse
- Automated quality evaluation (bonus feature)

---

## System Architecture

### High-Level Overview

```mermaid
flowchart TB
    subgraph Input["📥 Input Layer"]
        CLI["CLI Arguments<br/>--question"]
        STDIN["Piped Input<br/>stdin"]
        REPL["Interactive REPL<br/>prompt_toolkit"]
    end

    subgraph Orchestrator["🎯 Orchestrator"]
        IC["Intent Classifier<br/>(GPT-4o-mini)"]
        Router["Router<br/>(RunnableLambda)"]
    end

    subgraph Agents["🤖 Specialized RAG Agents"]
        HR["HR Agent<br/>📋 PTO, Benefits, Policies"]
        Tech["Tech Agent<br/>💻 VPN, Passwords, Hardware"]
        Finance["Finance Agent<br/>💰 Expenses, Payroll"]
        Legal["Legal Agent<br/>⚖️ Contracts, Compliance"]
    end

    subgraph VectorStores["📚 FAISS Vector Stores"]
        VS_HR["faiss_index/hr<br/>122 chunks"]
        VS_Tech["faiss_index/tech<br/>80 chunks"]
        VS_Finance["faiss_index/finance<br/>83 chunks"]
        VS_Legal["faiss_index/legal<br/>79 chunks"]
    end

    subgraph Output["📤 Output Layer"]
        Synth["Synthesizer<br/>(Multi-agent merge)"]
        Eval["Evaluator<br/>(Quality scoring)"]
        Response["Final Response"]
    end

    subgraph Observability["👁️ Observability"]
        LF["Langfuse<br/>Tracing & Scores"]
    end

    CLI --> IC
    STDIN --> IC
    REPL --> IC
    
    IC -->|"intents[]"| Router
    Router -->|"hr"| HR
    Router -->|"tech"| Tech
    Router -->|"finance"| Finance
    Router -->|"legal"| Legal
    
    HR <--> VS_HR
    Tech <--> VS_Tech
    Finance <--> VS_Finance
    Legal <--> VS_Legal
    
    HR --> Synth
    Tech --> Synth
    Finance --> Synth
    Legal --> Synth
    
    Synth --> Eval
    Eval --> Response
    
    IC -.->|trace| LF
    HR -.->|trace| LF
    Tech -.->|trace| LF
    Finance -.->|trace| LF
    Legal -.->|trace| LF
    Synth -.->|trace| LF
    Eval -.->|score| LF
```

### Request Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant O as Orchestrator
    participant C as Classifier
    participant R as Router
    participant A as RAG Agent(s)
    participant V as FAISS Index
    participant S as Synthesizer
    participant E as Evaluator
    participant L as Langfuse

    U->>O: Query: "How is PTO paid out?"
    O->>C: Classify intent
    C->>L: Log classification
    C-->>O: {intents: ["hr", "finance"]}
    
    O->>R: Route to agents
    
    par Parallel Agent Execution
        R->>A: HR Agent
        A->>V: Retrieve HR docs
        V-->>A: Top-k chunks
        A-->>R: HR answer + context
    and
        R->>A: Finance Agent
        A->>V: Retrieve Finance docs
        V-->>A: Top-k chunks
        A-->>R: Finance answer + context
    end
    
    R->>S: Merge answers
    S->>L: Log synthesis
    S-->>O: Unified answer
    
    O->>E: Evaluate quality
    E->>L: Report score (1-10)
    E-->>O: Evaluation result
    
    O-->>U: Final response + sources
```

---

## Component Details

### 1. Intent Classifier

The classifier uses GPT-4o-mini to perform **multi-label classification**, allowing queries to be routed to multiple departments simultaneously.

```mermaid
flowchart LR
    subgraph Input
        Q["User Query"]
    end
    
    subgraph Classification
        P["System Prompt<br/>(Category definitions)"]
        LLM["GPT-4o-mini<br/>temperature=0"]
        Parse["JSON Parser"]
    end
    
    subgraph Output
        I["intents: [hr, finance]"]
        R["reasoning: string"]
    end
    
    Q --> P
    P --> LLM
    LLM --> Parse
    Parse --> I
    Parse --> R
```

**Categories:**
| Intent | Description | Example Query |
|--------|-------------|---------------|
| `hr` | Time off, benefits, onboarding, conduct | "How do I request PTO?" |
| `tech` | Passwords, VPN, hardware, security | "How do I reset my password?" |
| `finance` | Expenses, payroll, budgets, vendors | "What's the expense policy?" |
| `legal` | Contracts, privacy, compliance, IP | "NDA signing process?" |
| `other` | Out of scope | "Best pizza in town?" |

### 2. RAG Agents

Each agent follows the same architecture pattern but with domain-specific configuration:

```mermaid
flowchart TB
    subgraph RAGAgent["RAG Agent Pattern"]
        Query["Query"]
        Retriever["FAISS Retriever<br/>k=4"]
        Context["Retrieved Context"]
        Prompt["Domain Prompt<br/>(System + Context + Query)"]
        LLM["GPT-4o-mini"]
        Answer["Answer + Sources"]
    end
    
    Query --> Retriever
    Retriever --> Context
    Context --> Prompt
    Query --> Prompt
    Prompt --> LLM
    LLM --> Answer
```

**Agent Configuration:**

| Agent | Documents | Chunks | Prompt Focus |
|-------|-----------|--------|--------------|
| HR | 8 files | 122 | Employee policies, benefits, procedures |
| Tech | 8 files | 80 | Technical support, troubleshooting |
| Finance | 10 files | 83 | Financial policies, expense rules |
| Legal | 12 files | 79 | Compliance, contracts, regulations |

### 3. Document Processing Pipeline

```mermaid
flowchart LR
    subgraph Source["Source Documents"]
        MD["Markdown Files<br/>data/*_docs/*.md"]
    end
    
    subgraph Processing["Processing"]
        Load["DirectoryLoader"]
        Split["RecursiveCharacterTextSplitter<br/>chunk_size=800<br/>overlap=200"]
        Embed["OpenAI Embeddings<br/>text-embedding-3-small"]
    end
    
    subgraph Storage["Vector Storage"]
        FAISS["FAISS Index<br/>faiss_index/{domain}/"]
    end
    
    MD --> Load
    Load --> Split
    Split --> Embed
    Embed --> FAISS
```

**Splitting Strategy:**
- **Chunk Size**: 800 characters (balances context and precision)
- **Overlap**: 200 characters (ensures continuity)
- **Separators**: `["\n## ", "\n### ", "\n\n", "\n", " "]` (respects document structure)

### 4. Synthesizer

When multiple agents respond, the synthesizer merges answers:

```mermaid
flowchart TB
    subgraph Inputs
        Q["Original Query"]
        HR_A["HR Answer"]
        FIN_A["Finance Answer"]
    end
    
    subgraph Synthesis
        Format["Format Responses<br/>=== HR ===<br/>=== FINANCE ==="]
        Prompt["Synthesis Prompt"]
        LLM["GPT-4o-mini"]
    end
    
    subgraph Output
        Final["Unified Answer<br/>(No redundancy,<br/>logically organized)"]
    end
    
    Q --> Prompt
    HR_A --> Format
    FIN_A --> Format
    Format --> Prompt
    Prompt --> LLM
    LLM --> Final
```

### 5. Evaluator (Bonus)

The evaluator scores responses on three dimensions:

```mermaid
flowchart LR
    subgraph Input
        Q["Query"]
        A["Answer"]
        C["Context"]
    end
    
    subgraph Evaluation
        LLM["GPT-4o-mini<br/>temperature=0"]
    end
    
    subgraph Scores["Scores (1-10)"]
        REL["Relevance<br/>Does it answer the question?"]
        COMP["Completeness<br/>Is it thorough?"]
        ACC["Accuracy<br/>Is it correct per context?"]
        TOTAL["Overall Score<br/>(average)"]
    end
    
    subgraph Report
        LF["Langfuse Score API"]
    end
    
    Q --> LLM
    A --> LLM
    C --> LLM
    LLM --> REL
    LLM --> COMP
    LLM --> ACC
    REL --> TOTAL
    COMP --> TOTAL
    ACC --> TOTAL
    TOTAL --> LF
```

---

## Data Flow Examples

### Example 1: Single-Domain Query

```mermaid
flowchart LR
    Q["How do I request PTO?"]
    C["Classifier"]
    HR["HR Agent"]
    R["Response about PTO policy"]
    
    Q --> C
    C -->|"intents: [hr]"| HR
    HR --> R
```

### Example 2: Multi-Domain Query

```mermaid
flowchart LR
    Q["How is unused PTO paid in my final paycheck?"]
    C["Classifier"]
    HR["HR Agent"]
    FIN["Finance Agent"]
    S["Synthesizer"]
    R["Combined response about<br/>PTO policy + payroll process"]
    
    Q --> C
    C -->|"intents: [hr, finance]"| HR
    C -->|"intents: [hr, finance]"| FIN
    HR --> S
    FIN --> S
    S --> R
```

### Example 3: Out-of-Scope Query

```mermaid
flowchart LR
    Q["What's the best pizza place?"]
    C["Classifier"]
    R["Sorry, this doesn't fit our<br/>HR, IT, Finance, or Legal departments."]
    
    Q --> C
    C -->|"intents: [other]"| R
```

---

## Langfuse Integration

### Trace Structure

```mermaid
flowchart TB
    subgraph Trace["Trace: User Query"]
        S1["Span: Intent Classification"]
        S2["Span: HR Agent"]
        S2a["Span: HR Retrieval"]
        S2b["Span: HR LLM"]
        S3["Span: Finance Agent"]
        S3a["Span: Finance Retrieval"]
        S3b["Span: Finance LLM"]
        S4["Span: Synthesis"]
        Score["Score: answer_quality = 8"]
    end
    
    S1 --> S2
    S1 --> S3
    S2 --> S2a
    S2a --> S2b
    S3 --> S3a
    S3a --> S3b
    S2b --> S4
    S3b --> S4
    S4 --> Score
```

### Captured Metrics

| Metric | Description |
|--------|-------------|
| Latency | Time per span and total |
| Token Usage | Input/output tokens per LLM call |
| Retrieved Docs | Documents returned by each retriever |
| Scores | Quality scores from evaluator |

---

## Technology Stack

```mermaid
mindmap
  root((Multi-Agent<br/>System))
    LangChain
      LCEL Runnables
      ChatPromptTemplate
      StrOutputParser
      RunnableLambda
    OpenAI
      GPT-4o-mini
      text-embedding-3-small
    FAISS
      Local persistence
      Similarity search
    Langfuse
      Tracing
      Score API
    Python
      prompt_toolkit
      python-dotenv
      pydantic
```

---

## Performance Characteristics

| Operation | Typical Latency | Notes |
|-----------|-----------------|-------|
| Intent Classification | 0.5-1s | Single LLM call |
| Document Retrieval | 10-50ms | FAISS in-memory search |
| RAG Agent Response | 1-2s | Retrieval + LLM |
| Multi-Agent Synthesis | 1-2s | Additional LLM call |
| **Total (single-domain)** | **2-3s** | |
| **Total (multi-domain)** | **4-6s** | Sequential execution |

### Optimization Opportunities

1. **Async Execution**: Run agents in parallel (currently sequential)
2. **Caching**: Cache embeddings and frequent query responses
3. **Streaming**: Stream responses for better UX
4. **Model Selection**: Use faster models for classification

---

## Security Considerations

| Aspect | Implementation |
|--------|----------------|
| API Keys | Stored in `.env`, never committed |
| Vector Store | Local files, no network exposure |
| User Input | Passed to LLM (prompt injection risk) |
| Data Privacy | Documents stored locally |

### Recommendations for Production

1. Add input sanitization
2. Implement rate limiting
3. Add authentication/authorization
4. Use managed vector store with access controls
5. Enable audit logging

---

## Conclusion

The Multi-Agent Routing System successfully demonstrates:

✅ **Intelligent Routing**: Multi-label classification handles complex, cross-domain queries  
✅ **Domain Isolation**: Separate FAISS indexes prevent knowledge contamination  
✅ **LangChain Best Practices**: LCEL runnables provide clean, maintainable code  
✅ **Full Observability**: Langfuse traces enable debugging and monitoring  
✅ **Quality Assurance**: Automated evaluation catches low-quality responses  

The architecture is designed for extensibility—adding new departments requires only creating a new agent module and updating the orchestrator's routing table.
