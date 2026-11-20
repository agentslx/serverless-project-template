"""Web search agent — uses Tavily to find relevant information."""
from __future__ import annotations

from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request

SYSTEM_PROMPT = """\
You are a web research specialist. Your job is to search the web for information
relevant to the user's query.

Guidelines:
- Search for the most authoritative and recent sources.
- Return structured findings with source URLs and titles.
- If a query is broad, break it into specific sub-queries.
- Always cite your sources.
"""


def create_web_search_agent(model_id: str, temperature: float = 0.3) -> Agent:
    model = BedrockModel(model_id=model_id, streaming=True, temperature=temperature)

    try:
        from strands_tools import web_search
        tools = [web_search, http_request]
    except ImportError:
        tools = [http_request]

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
    )
