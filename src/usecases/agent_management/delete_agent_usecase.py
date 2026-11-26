# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : delete_agent_usecase.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Dict, Optional

from core.services.participation_service import ParticipationService
from core.services.project_service import ProjectService


class DeleteAgentUseCase:
    """FN031/RG033: delete an agent of the project. The deletion cascades to
    all its participations and all its relationships (RG033); the removal
    counts are returned for the information message. The confirmation dialog
    is a UI responsibility: this use case executes without confirming.
    Adapted from planoscript's delete_agent_usecase."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, agent_id: int) -> Optional[Dict]:
        """Delete the agent; return True on success, False when refused."""
        project = self.project_service.current_project
        agent = ParticipationService.get_agent(project, agent_id)
        if agent is None:
            return None
        removed = ParticipationService.cascade_delete_agent(project, agent_id)  # RG033
        project.agent.remove(agent)
        self.project_service.set_modified(True)
        return {'agent': agent, 'removed': removed}
