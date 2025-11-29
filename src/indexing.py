"""
Document indexing module.

Loads documents from data directories, splits them into chunks,
embeds them using OpenAI embeddings, and persists to FAISS vector stores.

Usage:
    python -m src.indexing           # Index all domains
    python -m src.indexing --domain hr  # Index only HR domain
"""

import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    DOMAIN_CONFIG,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL_NAME,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_documents(docs_dir: Path) -> list:
    """
    Load all markdown documents from a directory.

    Args:
        docs_dir: Path to directory containing .md files.

    Returns:
        List of Document objects.
    """
    if not docs_dir.exists():
        logger.warning(f"Directory does not exist: {docs_dir}")
        return []

    loader = DirectoryLoader(
        str(docs_dir),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents from {docs_dir}")

    return documents


def split_documents(documents: list) -> list:
    """
    Split documents into chunks for embedding.

    Args:
        documents: List of Document objects.

    Returns:
        List of chunked Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    return chunks


def create_vector_store(chunks: list, persist_directory: Path, domain: str) -> FAISS:
    """
    Create and persist a FAISS vector store from document chunks.

    Args:
        chunks: List of chunked Document objects.
        persist_directory: Path to persist the FAISS index.
        domain: Name of the domain (for logging).

    Returns:
        FAISS vector store instance.
    """
    # Ensure directory exists
    persist_directory.mkdir(parents=True, exist_ok=True)

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

    # Create vector store
    logger.info(f"Creating FAISS index for '{domain}' at {persist_directory}")

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    # Save to disk
    vectorstore.save_local(str(persist_directory))

    logger.info(f"FAISS index for '{domain}' created with {len(chunks)} chunks")

    return vectorstore


def index_domain(domain: str) -> None:
    """
    Index a single domain: load docs, split, embed, persist.

    Args:
        domain: Domain name (hr, tech, finance, legal).
    """
    if domain not in DOMAIN_CONFIG:
        logger.error(f"Unknown domain: {domain}. Valid domains: {list(DOMAIN_CONFIG.keys())}")
        return

    config = DOMAIN_CONFIG[domain]
    docs_dir = config["docs_dir"]
    index_dir = config["index_dir"]

    logger.info(f"=== Indexing domain: {domain} ===")
    logger.info(f"Source: {docs_dir}")
    logger.info(f"Target: {index_dir}")

    # Load documents
    documents = load_documents(docs_dir)
    if not documents:
        logger.warning(f"No documents found for domain '{domain}'. Skipping.")
        return

    # Split into chunks
    chunks = split_documents(documents)
    if not chunks:
        logger.warning(f"No chunks generated for domain '{domain}'. Skipping.")
        return

    # Create and persist vector store
    create_vector_store(chunks, index_dir, domain)

    logger.info(f"=== Domain '{domain}' indexed successfully ===\n")


def index_all_domains() -> None:
    """Index all configured domains."""
    logger.info("Starting indexing for all domains...")

    for domain in DOMAIN_CONFIG:
        index_domain(domain)

    logger.info("All domains indexed successfully!")


def main():
    """Main entry point for the indexing script."""
    parser = argparse.ArgumentParser(
        description="Index documents into FAISS vector stores."
    )
    parser.add_argument(
        "--domain",
        "-d",
        type=str,
        choices=list(DOMAIN_CONFIG.keys()),
        help="Index only the specified domain. If not provided, indexes all domains.",
    )

    args = parser.parse_args()

    if args.domain:
        index_domain(args.domain)
    else:
        index_all_domains()


if __name__ == "__main__":
    main()
