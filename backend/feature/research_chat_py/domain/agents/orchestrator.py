"""Orchestrator agent — coordinates the research agent team."""
from __future__ import annotations

from strands import Agent
from strands.models import BedrockModel

from .config import get_agent_config
from .web_search_agent import create_web_search_agent
from .composing_agent import create_composing_agent

SYSTEM_PROMPT = """\
You are a research team orchestrator. You coordinate a team of specialist agents
to answer user questions thoroughly and accurately.

Your team:
1. **web_search_agent** — Searches the web for relevant information.
2. **composing_agent** — Synthesizes findings into a clear, well-sourced response.

Workflow:
1. Analyze the user's question to understand what information is needed.
2. Delegate research to web_search_agent with specific search queries.
3. Pass the research findings to composing_agent for final composition.
4. If the user explicitly requests a "report" or "document", instruct composing_agent
   to generate a comprehensive markdown report.

Always ensure responses are factual, well-sourced, and directly address the user's question.
"""


def create_orchestrator() -> Agent:
    """Create the orchestrator agent with dynamic config from AppConfig."""
    cfg = get_agent_config()
    model_id = cfg["model_id"]
    temperature = cfg.get("temperature", 0.3)

    model = BedrockModel(
        model_id=model_id,
        streaming=True,
        temperature=temperature,
        max_tokens=cfg.get("max_tokens", 4096),
    )

    web_search = create_web_search_agent(model_id, temperature)
    composer = create_composing_agent(model_id, temperature)

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[web_search, composer],
    )
