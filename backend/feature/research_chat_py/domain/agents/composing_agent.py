"""Composing agent — synthesizes research into a clear response or report."""
from __future__ import annotations

from strands import Agent
from strands.models import BedrockModel

SYSTEM_PROMPT = """\
You are a research writer and communicator. Your job is to take raw research findings
and compose them into clear, well-structured responses.

Guidelines:
- Synthesize information from multiple sources into a coherent narrative.
- Always include source citations with URLs.
- Use markdown formatting for readability.
- If asked to generate a report, produce a comprehensive markdown document with
  sections, headings, and a bibliography.
- Keep chat responses concise (2-4 paragraphs) unless a full report is requested.
"""


def create_composing_agent(model_id: str, temperature: float = 0.3) -> Agent:
    model = BedrockModel(model_id=model_id, streaming=True, temperature=temperature)
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[],
    )
