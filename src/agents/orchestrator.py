"""
Orchestrator module.

Handles intent classification and multi-agent routing:
1. Classifies user query into one or more departments (multi-label).
2. Routes to appropriate agent(s).
3. Synthesizes a unified answer when multiple agents respond.
"""

import json
import logging
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from src.config import (
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    INTENT_CATEGORIES,
    INTENT_DESCRIPTIONS,
)
from src.agents.hr_agent import get_hr_agent
from src.agents.tech_agent import get_tech_agent
from src.agents.finance_agent import get_finance_agent
from src.agents.legal_agent import get_legal_agent

logger = logging.getLogger(__name__)


# =============================================================================
# Intent Classification
# =============================================================================

class IntentClassification(BaseModel):
    """Schema for intent classification output."""
    intents: list[str] = Field(
        description="List of relevant department intents for the query"
    )
    reasoning: str = Field(
        description="Brief explanation of why these intents were selected"
    )


def get_classifier_chain() -> Runnable:
    """
    Create the intent classifier chain.

    Returns a chain that takes a query and outputs:
    - intents: List of relevant departments (e.g., ["hr", "finance"])
    - reasoning: Brief explanation of the classification
    """
    llm = ChatOpenAI(
        model=LLM_MODEL_NAME,
        temperature=0,  # Deterministic classification
    )

    # Build intent descriptions for the prompt
    intent_desc = "\n".join([
        f"- {intent}: {INTENT_DESCRIPTIONS[intent]}"
        for intent in INTENT_CATEGORIES
    ])

    system_prompt = f"""You are an intent classifier for an enterprise support system.
Your job is to analyze user queries and determine which department(s) should handle them.

Available departments:
{intent_desc}

IMPORTANT RULES:
1. A query can be relevant to MULTIPLE departments. For example:
   - "How is PTO paid in my final paycheck?" → ["hr", "finance"]
   - "What are the data privacy requirements for vendor contracts?" → ["legal"]
2. Return ALL relevant departments, not just the primary one.
3. Only return "other" if the query truly doesn't fit any department.
4. Be inclusive rather than exclusive - if in doubt, include the department.

Respond with valid JSON only, no markdown formatting:
{{{{"intents": ["dept1", "dept2"], "reasoning": "brief explanation"}}}}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Query: {query}"),
    ])

    def parse_response(response: str) -> dict:
        """Parse the LLM response into structured output."""
        try:
            # Clean up response (remove markdown if present)
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            cleaned = cleaned.strip()

            result = json.loads(cleaned)

            # Validate intents
            valid_intents = [
                intent for intent in result.get("intents", [])
                if intent in INTENT_CATEGORIES
            ]

            # Ensure at least one intent
            if not valid_intents:
                valid_intents = ["other"]

            return {
                "intents": valid_intents,
                "reasoning": result.get("reasoning", ""),
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse classifier response: {e}")
            return {
                "intents": ["other"],
                "reasoning": "Failed to parse classification",
            }

    chain = prompt | llm | StrOutputParser() | RunnableLambda(parse_response)

    return chain


def classify_intent(query: str) -> dict:
    """
    Classify a query's intent.

    Args:
        query: User query string.

    Returns:
        Dict with 'intents' (list) and 'reasoning' (str).
    """
    classifier = get_classifier_chain()
    return classifier.invoke({"query": query})


# =============================================================================
# Agent Registry
# =============================================================================

# Lazy loading of agents to avoid initialization until needed
_agents_cache: dict[str, Runnable] = {}


class AgentNotAvailableError(Exception):
    """Raised when an agent cannot be loaded (e.g., missing vector store)."""
    pass


def get_agent(domain: str) -> Runnable:
    """
    Get an agent for the specified domain.

    Args:
        domain: Domain name (hr, tech, finance, legal).

    Returns:
        The domain's RAG agent.

    Raises:
        AgentNotAvailableError: If agent cannot be loaded.
        KeyError: If domain is not recognized.
    """
    if domain in _agents_cache:
        return _agents_cache[domain]

    agent_factories = {
        "hr": get_hr_agent,
        "tech": get_tech_agent,
        "finance": get_finance_agent,
        "legal": get_legal_agent,
    }

    factory = agent_factories.get(domain)
    if not factory:
        raise KeyError(f"Unknown domain: {domain}")

    try:
        agent = factory()
        _agents_cache[domain] = agent
        return agent
    except FileNotFoundError as e:
        raise AgentNotAvailableError(str(e)) from e


# =============================================================================
# Synthesizer
# =============================================================================

def get_synthesizer_chain() -> Runnable:
    """
    Create the synthesizer chain for merging multiple agent responses.

    Takes answers from multiple agents and produces a unified response.
    """
    llm = ChatOpenAI(
        model=LLM_MODEL_NAME,
        temperature=LLM_TEMPERATURE,
    )

    system_prompt = """You are a response synthesizer for an enterprise support system.
You receive answers from multiple specialized departments and must combine them into
a single, coherent, helpful response.

Guidelines:
1. Integrate information from all sources smoothly.
2. Avoid redundancy - don't repeat the same information.
3. Organize the response logically.
4. If sources provide conflicting information, note this and suggest clarification.
5. Maintain a professional, helpful tone.
6. Reference which department provided specific information when relevant."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Original question: {query}

Responses from departments:
{agent_responses}

Please synthesize these into a single, comprehensive answer."""),
    ])

    chain = prompt | llm | StrOutputParser()

    return chain


# =============================================================================
# Orchestrator
# =============================================================================

def route_and_execute(state: dict) -> dict:
    """
    Route query to appropriate agents and execute.

    Args:
        state: Dict containing 'query', 'intents', and 'reasoning'.

    Returns:
        Dict with query results including answers and sources.
    """
    query = state["query"]
    intents = state["intents"]
    reasoning = state["reasoning"]

    logger.info(f"Routing query to intents: {intents}")
    logger.debug(f"Classification reasoning: {reasoning}")

    # Handle 'other' intent
    if intents == ["other"]:
        return {
            "query": query,
            "intents": intents,
            "reasoning": reasoning,
            "agent_responses": [],
            "final_answer": "I'm sorry, but your question doesn't seem to fit into our "
                           "HR, IT Support, Finance, or Legal departments. Please try "
                           "rephrasing your question or contact the main support line.",
            "sources": [],
            "context": "",
        }

    # Execute each relevant agent
    agent_responses = []
    all_sources = []
    missing_indexes = []

    for intent in intents:
        if intent == "other":
            continue

        try:
            agent = get_agent(intent)
            logger.info(f"Invoking {intent} agent...")
            result = agent.invoke({"query": query})

            agent_responses.append({
                "department": intent,
                "answer": result.get("answer", ""),
                "context": result.get("context", ""),
            })

            # Collect sources
            retrieved_docs = result.get("retrieved_docs", [])
            for doc in retrieved_docs:
                source = doc.metadata.get("source", "Unknown")
                if source not in all_sources:
                    all_sources.append(source)

        except AgentNotAvailableError as e:
            logger.error(f"Agent for '{intent}' not available: {e}")
            missing_indexes.append(intent)

        except Exception as e:
            logger.error(f"Error invoking {intent} agent: {e}")
            agent_responses.append({
                "department": intent,
                "answer": f"Error retrieving information from {intent} department.",
                "context": "",
            })

    # Handle missing indexes - provide helpful error message
    if missing_indexes and not agent_responses:
        missing_list = ", ".join(missing_indexes)
        final_answer = (
            f"⚠️ **Vector store not found** for: {missing_list}\n\n"
            f"The knowledge base has not been indexed yet. Please run:\n\n"
            f"```\nacme-index\n```\n\n"
            f"Or: `python -m src.indexing`\n\n"
            f"This will create the FAISS indexes needed to answer your question."
        )
        return {
            "query": query,
            "intents": intents,
            "reasoning": reasoning,
            "agent_responses": [],
            "final_answer": final_answer,
            "sources": [],
            "context": "",
            "error": "missing_index",
        }

    # Synthesize if multiple responses
    if len(agent_responses) > 1:
        logger.info("Synthesizing responses from multiple agents...")
        synthesizer = get_synthesizer_chain()

        # Format agent responses for synthesizer
        formatted_responses = "\n\n".join([
            f"=== {resp['department'].upper()} Department ===\n{resp['answer']}"
            for resp in agent_responses
        ])

        final_answer = synthesizer.invoke({
            "query": query,
            "agent_responses": formatted_responses,
        })
    elif len(agent_responses) == 1:
        final_answer = agent_responses[0]["answer"]
    else:
        final_answer = "I couldn't find relevant information to answer your question."

    # Consolidate context from all agents for evaluation
    consolidated_context = "\n\n".join([
        resp["context"] for resp in agent_responses if resp.get("context")
    ])

    return {
        "query": query,
        "intents": intents,
        "reasoning": reasoning,
        "agent_responses": agent_responses,
        "final_answer": final_answer,
        "sources": all_sources,
        "context": consolidated_context,
    }


def get_orchestrator() -> Runnable:
    """
    Create the full orchestrator chain.

    The orchestrator:
    1. Classifies intent(s) from the query.
    2. Routes to appropriate agent(s).
    3. Synthesizes answers if multiple agents respond.

    Returns:
        A LangChain Runnable that takes {"query": str} and returns full results.
    """
    classifier = get_classifier_chain()

    def add_query_to_classification(inputs: dict) -> dict:
        """Add original query to classification results."""
        query = inputs["query"]
        classification = classifier.invoke({"query": query})
        return {
            "query": query,
            "intents": classification["intents"],
            "reasoning": classification["reasoning"],
        }

    orchestrator = (
        RunnableLambda(add_query_to_classification)
        | RunnableLambda(route_and_execute)
    )

    return orchestrator
