"""
Finance Agent module.

Specialized RAG agent for Finance queries:
- Expense reports and reimbursements
- Corporate cards and travel
- Payroll and compensation
- Purchasing and vendor payments
- Budgets and approvals
"""

from langchain_core.runnables import Runnable

from src.config import DOMAIN_CONFIG
from src.agents.base_agent import (
    load_vector_store,
    create_rag_agent,
    get_domain_system_prompt,
)


def get_finance_agent() -> Runnable:
    """
    Create and return the Finance RAG agent.

    Returns:
        A LangChain Runnable that handles Finance-related queries.

    Raises:
        FileNotFoundError: If the Finance vector store has not been created.
    """
    config = DOMAIN_CONFIG["finance"]

    # Load the persisted vector store
    vectorstore = load_vector_store(
        persist_directory=config["index_dir"],
        domain_name="finance",
    )

    # Get domain-specific system prompt
    system_prompt = get_domain_system_prompt("finance")

    # Create and return the RAG agent
    agent = create_rag_agent(
        vectorstore=vectorstore,
        domain_name="finance",
        system_prompt=system_prompt,
    )

    return agent
