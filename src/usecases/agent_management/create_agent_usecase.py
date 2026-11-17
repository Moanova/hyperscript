# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : create_agent_usecase.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import AGENT_TYPES, Agent
from core.services.project_service import ProjectService


class CreateAgentUseCase:
    """FN031: create an agent of the project (project-level entity, SU008).

    The agent gets a project-unique integer ID, a label (default
    "Agent {id}"), a type (Character or Artefact, AGENT_TYPES) and optional
    note and narrative content. Adapted from planoscript's create_agent_usecase.
    """

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, lb: Optional[str] = None, typ: str = "Character",
                note: Optional[str] = None, content: Optional[str] = None) -> Agent:
        if typ not in AGENT_TYPES:
            raise ValueError(f"Invalid Agent.typ: {typ}. Must be one of: {AGENT_TYPES}")
        project = self.project_service.current_project
        entity_id = project.get_next_id('agent')
        agent = Agent(
            id=entity_id,
            lb=(lb.strip() if isinstance(lb, str) and lb.strip() else f"Agent {entity_id}"),
            typ=typ,
            note=(note if note and note.strip() else None),
            content=(content if content and content.strip() else None),
        )
        project.agent.append(agent)
        self.project_service.set_modified(True)
        return agent
