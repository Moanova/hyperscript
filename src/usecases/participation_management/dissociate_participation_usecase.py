# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : dissociate_participation_usecase.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Participation
from core.services.participation_service import ParticipationService
from core.services.project_service import ProjectService


class DissociateParticipationUseCase:
    """FN030: remove the participation between an agent and a block of the
    current narrative map. Returns the removed participation, or None when
    no such participation exists. Adapted from planoscript's
    dissociate_agent_state_usecase."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, agent_id: int, block_id: int) -> Optional[Participation]:
        project = self.project_service.current_project
        narrative_map = project.narrative_maps[0]  # MVP: single map
        if ParticipationService.get_agent(project, agent_id) is None:
            raise ValueError(f"Agent {agent_id} not found in the project")
        if ParticipationService.get_block(narrative_map, block_id) is None:
            raise ValueError(f"Block {block_id} not found in the narrative map")
        existing = ParticipationService.find_participation(narrative_map, block_id, agent_id)
        if existing is None:
            return None
        narrative_map.participation.remove(existing)
        self.project_service.set_modified(True)
        return existing
