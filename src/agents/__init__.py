"""
Agents package.

Contains specialized RAG agents for each domain and the orchestrator
that routes queries to the appropriate agent(s).
"""

from src.agents.base_agent import create_rag_agent, load_vector_store
from src.agents.hr_agent import get_hr_agent
from src.agents.tech_agent import get_tech_agent
from src.agents.finance_agent import get_finance_agent
from src.agents.legal_agent import get_legal_agent
from src.agents.orchestrator import get_orchestrator, classify_intent

__all__ = [
    "create_rag_agent",
    "load_vector_store",
    "get_hr_agent",
    "get_tech_agent",
    "get_finance_agent",
    "get_legal_agent",
    "get_orchestrator",
    "classify_intent",
]
