"""
Tech/IT Agent module.

Specialized RAG agent for IT Support queries:
- Account and password management
- VPN and remote access
- Hardware and software requests
- Troubleshooting
- IT security policies
"""

from langchain_core.runnables import Runnable

from src.config import DOMAIN_CONFIG
from src.agents.base_agent import (
    load_vector_store,
    create_rag_agent,
    get_domain_system_prompt,
)


def get_tech_agent() -> Runnable:
    """
    Create and return the Tech/IT RAG agent.

    Returns:
        A LangChain Runnable that handles IT-related queries.

    Raises:
        FileNotFoundError: If the Tech vector store has not been created.
    """
    config = DOMAIN_CONFIG["tech"]

    # Load the persisted vector store
    vectorstore = load_vector_store(
        persist_directory=config["index_dir"],
        domain_name="tech",
    )

    # Get domain-specific system prompt
    system_prompt = get_domain_system_prompt("tech")

    # Create and return the RAG agent
    agent = create_rag_agent(
        vectorstore=vectorstore,
        domain_name="tech",
        system_prompt=system_prompt,
    )

    return agent
