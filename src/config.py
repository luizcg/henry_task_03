"""
Configuration settings for the multi-agent system.

Centralizes paths, model names, and parameters used across modules.
"""

import os
from pathlib import Path

# =============================================================================
# Project Paths
# =============================================================================

# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories (source documents)
DATA_DIR = PROJECT_ROOT / "data"
HR_DOCS_DIR = DATA_DIR / "hr_docs"
TECH_DOCS_DIR = DATA_DIR / "tech_docs"
FINANCE_DOCS_DIR = DATA_DIR / "finance_docs"
LEGAL_DOCS_DIR = DATA_DIR / "legal_docs"

# Vector store directories (FAISS persistence)
FAISS_BASE_DIR = PROJECT_ROOT / "faiss_index"
HR_FAISS_DIR = FAISS_BASE_DIR / "hr"
TECH_FAISS_DIR = FAISS_BASE_DIR / "tech"
FINANCE_FAISS_DIR = FAISS_BASE_DIR / "finance"
LEGAL_FAISS_DIR = FAISS_BASE_DIR / "legal"

# Mapping of domain names to their paths
DOMAIN_CONFIG = {
    "hr": {
        "docs_dir": HR_DOCS_DIR,
        "index_dir": HR_FAISS_DIR,
        "description": "Human Resources: PTO, benefits, onboarding, performance, policies",
    },
    "tech": {
        "docs_dir": TECH_DOCS_DIR,
        "index_dir": TECH_FAISS_DIR,
        "description": "IT Support: account access, VPN, hardware, software, troubleshooting",
    },
    "finance": {
        "docs_dir": FINANCE_DOCS_DIR,
        "index_dir": FINANCE_FAISS_DIR,
        "description": "Finance: expenses, reimbursements, payroll, budgets, purchasing",
    },
    "legal": {
        "docs_dir": LEGAL_DOCS_DIR,
        "index_dir": LEGAL_FAISS_DIR,
        "description": "Legal: contracts, privacy, compliance, IP, records retention",
    },
}

# =============================================================================
# Model Configuration
# =============================================================================

# LLM settings
LLM_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
LLM_TEMPERATURE = 0.0  # Deterministic for consistent answers

# Embedding settings
EMBEDDING_MODEL_NAME = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# =============================================================================
# Text Splitting Configuration
# =============================================================================

CHUNK_SIZE = 800  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# =============================================================================
# Retrieval Configuration
# =============================================================================

RETRIEVER_K = 4  # Number of documents to retrieve per query

# =============================================================================
# Intent Categories
# =============================================================================

INTENT_CATEGORIES = ["hr", "tech", "finance", "legal", "other"]

INTENT_DESCRIPTIONS = {
    "hr": "Questions about time off, PTO, benefits, onboarding, performance reviews, HR policies, employee handbook",
    "tech": "Questions about password reset, account access, VPN, hardware requests, software, IT troubleshooting, security",
    "finance": "Questions about expense reports, reimbursements, corporate cards, payroll, budgets, purchasing, invoices",
    "legal": "Questions about contracts, NDAs, privacy, data protection, compliance, intellectual property, legal holds",
    "other": "Questions that don't fit into HR, Tech, Finance, or Legal categories",
}
