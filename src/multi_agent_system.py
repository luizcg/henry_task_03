"""
Multi-Agent System - Main Entrypoint.

Supports three modes of operation:
1. Single question via CLI argument: --question "..."
2. Question via stdin (piped input)
3. Interactive REPL (default when no input)

Usage:
    python -m src.multi_agent_system --question "How do I request PTO?"
    echo "How do I reset my password?" | python -m src.multi_agent_system
    python -m src.multi_agent_system  # Interactive REPL
"""

import argparse
import json
import logging
import sys
from typing import Optional

from dotenv import load_dotenv

# Load environment variables before other imports
load_dotenv()

# Try to import Langfuse, but make it optional
LANGFUSE_AVAILABLE = False
LANGFUSE_ERROR = None
LangfuseCallbackHandler = None

try:
    # Try langfuse.callback first (langfuse-langchain package)
    from langfuse.callback import CallbackHandler as LangfuseCallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    try:
        # Fallback to langfuse.langchain (some versions)
        from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
        LANGFUSE_AVAILABLE = True
    except ImportError:
        LANGFUSE_ERROR = "langfuse-langchain not installed"
except Exception as e:
    LANGFUSE_ERROR = f"Langfuse import error: {e}"

from src.agents.orchestrator import get_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Langfuse Integration
# =============================================================================

def get_langfuse_handler():
    """
    Create a Langfuse callback handler if credentials are configured.

    Returns:
        LangfuseCallbackHandler or None if not available/configured.
    """
    if not LANGFUSE_AVAILABLE:
        logger.info(f"Langfuse not available: {LANGFUSE_ERROR}")
        return None

    try:
        handler = LangfuseCallbackHandler()
        logger.info("Langfuse tracing enabled")
        return handler
    except Exception as e:
        logger.warning(f"Langfuse not configured: {e}")
        return None


# =============================================================================
# Query Execution
# =============================================================================

def run_query(query: str, langfuse_handler: Optional[LangfuseCallbackHandler] = None) -> dict:
    """
    Execute a query through the orchestrator.

    Args:
        query: User question.
        langfuse_handler: Optional Langfuse handler for tracing.

    Returns:
        Dict with query results.
    """
    orchestrator = get_orchestrator()

    # Prepare config with callbacks if Langfuse is available
    config = {}
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]

    result = orchestrator.invoke({"query": query}, config=config)

    return result


def format_response(result: dict, as_json: bool = False) -> str:
    """
    Format the orchestrator result for display.

    Args:
        result: Dict from orchestrator.
        as_json: If True, return JSON output for piping.

    Returns:
        Formatted string for console output.
    """
    if as_json:
        output = {
            "query": result.get("query", ""),
            "intents": result.get("intents", []),
            "reasoning": result.get("reasoning", ""),
            "final_answer": result.get("final_answer", ""),
            "sources": result.get("sources", []),
            "context": result.get("context", ""),
        }
        if result.get("error"):
            output["error"] = result.get("error")
        return json.dumps(output, ensure_ascii=False, indent=2)

    lines = []

    # Check for setup errors first
    if result.get("error") == "missing_index":
        lines.append("\n⚠️  Vector store not found!")
        lines.append("")
        lines.append("The knowledge base has not been indexed yet.")
        lines.append("Please run one of these commands:")
        lines.append("")
        lines.append("    acme-index")
        lines.append("    python -m src.indexing")
        lines.append("")
        lines.append("This will create the FAISS indexes needed to answer questions.")
        return "\n".join(lines)

    # Classification info
    intents = result.get("intents", [])
    reasoning = result.get("reasoning", "")

    lines.append(f"\n📋 Classification: {', '.join(intents)}")
    if reasoning:
        lines.append(f"   Reasoning: {reasoning}")

    # Main answer
    lines.append(f"\n💬 Answer:\n{result.get('final_answer', 'No answer available')}")

    # Sources
    sources = result.get("sources", [])
    if sources:
        lines.append(f"\n📚 Sources:")
        for source in sources[:5]:  # Limit to 5 sources
            lines.append(f"   - {source}")

    return "\n".join(lines)


# =============================================================================
# Single Query Mode
# =============================================================================

def run_single_query(query: str, as_json: bool = False) -> None:
    """
    Run a single query and print the result.

    Args:
        query: User question.
        as_json: If True, output JSON for piping to evaluator.
    """
    if not as_json:
        logger.info(f"Processing query: {query[:50]}...")

    handler = get_langfuse_handler()

    try:
        result = run_query(query, handler)
        print(format_response(result, as_json=as_json))
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        # Flush Langfuse events
        if handler:
            handler.flush()


# =============================================================================
# Interactive REPL Mode
# =============================================================================

def run_repl() -> None:
    """
    Run an interactive REPL session using prompt_toolkit.
    """
    try:
        from prompt_toolkit import prompt
        from prompt_toolkit.history import InMemoryHistory
    except ImportError:
        logger.warning("prompt_toolkit not installed, using basic input()")
        run_basic_repl()
        return

    print("\n🤖 Acme Corporation Support Assistant")
    print("=" * 40)
    print("Ask questions about HR, IT, Finance, or Legal.")
    print("Type 'exit' or 'quit' to leave.\n")

    handler = get_langfuse_handler()
    history = InMemoryHistory()

    while True:
        try:
            query = prompt(
                "acme-assistant> ",
                history=history,
            ).strip()

            if not query:
                continue

            if query.lower() in {"exit", "quit", "q"}:
                print("\nGoodbye! 👋")
                break

            result = run_query(query, handler)
            print(format_response(result))
            print()  # Blank line for readability

        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"\n❌ Error: {e}\n")

    # Flush Langfuse events
    if handler:
        handler.flush()


def run_basic_repl() -> None:
    """
    Basic REPL fallback using standard input().
    """
    print("\n🤖 Acme Corporation Support Assistant")
    print("=" * 40)
    print("Ask questions about HR, IT, Finance, or Legal.")
    print("Type 'exit' or 'quit' to leave.\n")

    handler = get_langfuse_handler()

    while True:
        try:
            query = input("acme-assistant> ").strip()

            if not query:
                continue

            if query.lower() in {"exit", "quit", "q"}:
                print("\nGoodbye! 👋")
                break

            result = run_query(query, handler)
            print(format_response(result))
            print()

        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"\n❌ Error: {e}\n")

    if handler:
        handler.flush()


# =============================================================================
# Main Entry Point
# =============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Acme Corporation Multi-Agent Support System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single question via CLI
    python -m src.multi_agent_system -q "How do I request PTO?"

    # Piped input
    echo "What is the VPN setup process?" | python -m src.multi_agent_system

    # Interactive REPL
    python -m src.multi_agent_system
        """,
    )

    parser.add_argument(
        "--question", "-q",
        type=str,
        help="Single question to ask the system",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format (for piping to evaluator)",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Mode 1: CLI argument
    if args.question:
        run_single_query(args.question, as_json=args.json)
        return

    # Mode 2: Piped stdin
    if not sys.stdin.isatty():
        query = sys.stdin.read().strip()
        if query:
            run_single_query(query)
            return
        else:
            logger.warning("Empty input from stdin")
            return

    # Mode 3: Interactive REPL
    run_repl()


if __name__ == "__main__":
    main()
