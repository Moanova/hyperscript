# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : update_agent_usecase.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from datetime import datetime
from typing import Optional

from core.models.data_model import AGENT_TYPES, Agent
from core.services.project_service import ProjectService


class UpdateAgentUseCase:
    """FN031: edit an agent's editable attributes (label, type, note, narrative
    content). Adapted from planoscript's update_agent_usecase."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, agent: Agent, lb: Optional[str] = None, typ: Optional[str] = None,
                note: Optional[str] = None, content: Optional[str] = None) -> Agent:
        # None means "unchanged"; pass "" to clear a field
        if lb is not None:
            if not lb.strip():
                raise ValueError("Agent label cannot be empty")  # FN031
            agent.lb = lb.strip()
        if typ is not None:
            if typ not in AGENT_TYPES:
                raise ValueError(f"Invalid Agent.typ: {typ}. Must be one of: {AGENT_TYPES}")
            agent.typ = typ
        if note is not None:
            agent.note = note if note.strip() else None
        if content is not None:
            agent.content = content if content.strip() else None
        agent.modification_date_time = datetime.now()
        self.project_service.set_modified(True)
        return agent
