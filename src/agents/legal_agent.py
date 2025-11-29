"""
Legal Agent module.

Specialized RAG agent for Legal queries:
- Contract approval and signing
- Privacy and data protection
- Intellectual property and confidentiality
- Compliance and ethics
- Records retention and legal holds
"""

from langchain_core.runnables import Runnable

from src.config import DOMAIN_CONFIG
from src.agents.base_agent import (
    load_vector_store,
    create_rag_agent,
    get_domain_system_prompt,
)


def get_legal_agent() -> Runnable:
    """
    Create and return the Legal RAG agent.

    Returns:
        A LangChain Runnable that handles Legal-related queries.

    Raises:
        FileNotFoundError: If the Legal vector store has not been created.
    """
    config = DOMAIN_CONFIG["legal"]

    # Load the persisted vector store
    vectorstore = load_vector_store(
        persist_directory=config["index_dir"],
        domain_name="legal",
    )

    # Get domain-specific system prompt
    system_prompt = get_domain_system_prompt("legal")

    # Create and return the RAG agent
    agent = create_rag_agent(
        vectorstore=vectorstore,
        domain_name="legal",
        system_prompt=system_prompt,
    )

    return agent
