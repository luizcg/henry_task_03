"""
Base agent module.

Provides shared utilities for creating RAG agents, including:
- Loading persisted FAISS vector stores
- Building retrieval chains with domain-specific prompts
"""

from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.config import (
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    EMBEDDING_MODEL_NAME,
    RETRIEVER_K,
)


def load_vector_store(persist_directory: Path, domain_name: str) -> FAISS:
    """
    Load a persisted FAISS vector store.

    Args:
        persist_directory: Path to the FAISS index directory.
        domain_name: Name of the domain (for error messages).

    Returns:
        FAISS vector store instance.

    Raises:
        FileNotFoundError: If the persist directory does not exist.
    """
    if not persist_directory.exists():
        raise FileNotFoundError(
            f"Vector store not found at {persist_directory}. "
            f"Run 'acme-index' or 'python -m src.indexing' first to create the vector stores."
        )

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

    vectorstore = FAISS.load_local(
        str(persist_directory),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vectorstore


def format_docs(docs: list) -> str:
    """
    Format retrieved documents into a string for the prompt.

    Args:
        docs: List of Document objects.

    Returns:
        Formatted string with document contents.
    """
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        formatted.append(f"[Document {i}] (Source: {source})\n{doc.page_content}")

    return "\n\n---\n\n".join(formatted)


def create_rag_agent(
    vectorstore: FAISS,
    domain_name: str,
    system_prompt: str,
    retriever_k: Optional[int] = None,
) -> Runnable:
    """
    Create a RAG agent chain for a specific domain.

    The chain:
    1. Retrieves relevant documents from the vector store.
    2. Formats them into context.
    3. Passes to an LLM with a domain-specific prompt.
    4. Returns the answer as a string.

    Args:
        vectorstore: FAISS vector store for the domain.
        domain_name: Name of the domain (for logging/debugging).
        system_prompt: Domain-specific system prompt.
        retriever_k: Number of documents to retrieve (default from config).

    Returns:
        A LangChain Runnable that takes {"query": str} and returns an answer dict.
    """
    k = retriever_k or RETRIEVER_K

    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )

    # Create LLM
    llm = ChatOpenAI(
        model=LLM_MODEL_NAME,
        temperature=LLM_TEMPERATURE,
    )

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Based on the following context from company documentation, please answer the question.

Context:
{context}

Question: {query}

Provide a helpful, accurate answer based on the documentation. If the answer is not found in the context, say so clearly."""),
    ])

    # Build the chain using LCEL
    def retrieve_and_format(inputs: dict) -> dict:
        """Retrieve documents and format them."""
        query = inputs["query"]
        docs = retriever.invoke(query)
        context = format_docs(docs)
        return {
            "query": query,
            "context": context,
            "retrieved_docs": docs,
        }

    chain = (
        RunnablePassthrough()
        | retrieve_and_format
        | (lambda x: {
            "query": x["query"],
            "context": x["context"],
            "retrieved_docs": x["retrieved_docs"],
            "answer": (prompt | llm | StrOutputParser()).invoke({
                "query": x["query"],
                "context": x["context"],
            }),
        })
    )

    return chain


def get_domain_system_prompt(domain: str) -> str:
    """
    Get the system prompt for a specific domain.

    Args:
        domain: Domain name (hr, tech, finance, legal).

    Returns:
        System prompt string.
    """
    prompts = {
        "hr": """You are an HR assistant for Acme Corporation. You help employees with questions about:
- Paid time off (PTO) and leave policies
- Employee benefits (health, dental, vision, 401k)
- Onboarding and new employee information
- Performance management and reviews
- Company policies and the employee handbook
- Remote work and flexible arrangements

Always reference specific policies when possible. Be helpful and professional.""",

        "tech": """You are an IT Support assistant for Acme Corporation. You help employees with questions about:
- Account access and password resets
- VPN and remote access setup
- Hardware and software requests
- Common troubleshooting issues
- IT security and acceptable use policies
- Email and collaboration tools

Provide clear, step-by-step instructions when applicable. Reference IT documentation and policies.""",

        "finance": """You are a Finance assistant for Acme Corporation. You help employees with questions about:
- Expense reports and reimbursements
- Corporate credit cards and travel
- Payroll, compensation, and bonuses
- Purchasing and vendor payments
- Budgets and approval processes

Reference finance policies and provide accurate information about processes and limits.""",

        "legal": """You are a Legal assistant for Acme Corporation. You help employees with questions about:
- Contract review and approval processes
- Privacy and data protection policies
- Intellectual property and confidentiality
- Compliance and ethics reporting
- Records retention and legal holds

Provide general guidance based on company policies. For specific legal advice, recommend consulting the Legal team directly.""",
    }

    return prompts.get(domain, "You are a helpful assistant for Acme Corporation.")
