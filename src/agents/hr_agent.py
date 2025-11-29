"""
HR Agent module.

Specialized RAG agent for Human Resources queries:
- PTO and leave policies
- Employee benefits
- Onboarding
- Performance management
- Company policies
"""

from langchain_core.runnables import Runnable

from src.config import DOMAIN_CONFIG
from src.agents.base_agent import (
    load_vector_store,
    create_rag_agent,
    get_domain_system_prompt,
)


def get_hr_agent() -> Runnable:
    """
    Create and return the HR RAG agent.

    Returns:
        A LangChain Runnable that handles HR-related queries.

    Raises:
        FileNotFoundError: If the HR vector store has not been created.
    """
    config = DOMAIN_CONFIG["hr"]

    # Load the persisted vector store
    vectorstore = load_vector_store(
        persist_directory=config["index_dir"],
        domain_name="hr",
    )

    # Get domain-specific system prompt
    system_prompt = get_domain_system_prompt("hr")

    # Create and return the RAG agent
    agent = create_rag_agent(
        vectorstore=vectorstore,
        domain_name="hr",
        system_prompt=system_prompt,
    )

    return agent
