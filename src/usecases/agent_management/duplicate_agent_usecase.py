# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : duplicate_agent_usecase.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Agent
from core.services.project_service import ProjectService


class DuplicateAgentUseCase:
    """FN031: duplicate an agent - new project-unique ID, distinct label
    ("{lb} (copy)" by default), editable attributes inherited. The
    participations and relationships of the source are NOT copied (same
    principle as block duplication). Adapted from planoscript's
    duplicate_agent_usecase."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, source: Agent, lb: Optional[str] = None) -> Agent:
        """Duplicate the agent; return the copy, or None when refused."""
        project = self.project_service.current_project
        if source not in project.agent:
            raise ValueError(f"Agent {source.id} not found in the project")
        entity_id = project.get_next_id('agent')
        copy = Agent(
            id=entity_id,
            lb=(lb.strip() if isinstance(lb, str) and lb.strip() else f"{source.lb} (copy)"),
            typ=source.typ,
            note=source.note,
            content=source.content,
        )
        project.agent.append(copy)
        self.project_service.set_modified(True)
        return copy
