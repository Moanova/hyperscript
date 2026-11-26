# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : associate_participation_usecase.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.models.data_model import Participation
from core.services.participation_service import ParticipationService
from core.services.project_service import ProjectService


class AssociateParticipationUseCase:
    """FN030/RG032: associate an agent with a block of the current narrative
    map (the participation is symmetric, SU008). Idempotent: when the pair
    (block, agent) is already participating (RG032), the existing
    participation is returned unchanged. Adapted from planoscript's
    associate_agent_state_usecase. The participation note is not editable
    in the MVP."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, agent_id: int, block_id: int) -> Participation:
        """Create the participation (agent on block); return it, or None when it exists."""
        project = self.project_service.current_project
        narrative_map = project.narrative_maps[0]  # MVP: single map
        agent = ParticipationService.get_agent(project, agent_id)
        block = ParticipationService.get_block(narrative_map, block_id)
        if agent is None:
            raise ValueError(f"Agent {agent_id} not found in the project")
        if block is None:
            raise ValueError(f"Block {block_id} not found in the narrative map")
        existing = ParticipationService.find_participation(narrative_map, block_id, agent_id)
        if existing is not None:  # RG032: unique participation per (block, agent)
            return existing
        participation = Participation(
            id=narrative_map.get_next_id('participation'),
            block_id=block_id,
            agent_id=agent_id,
        )
        narrative_map.participation.append(participation)
        self.project_service.set_modified(True)
        return participation
