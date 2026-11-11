# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : create_transition_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Transition
from core.services.project_service import ProjectService
from core.services.transition_service import TransitionService
from core.services.journey_sequence_service import JourneySequenceService


class CreateTransitionUseCase:
    """FN020: create a directed transition between two blocks. Creation is
    refused when RG028 forbids it (block-type matrix or duplicate ordered
    pair); cycles are allowed. Returns None when refused."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, from_block_id: int, to_block_id: int, note: Optional[str] = None) -> Optional[Transition]:
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        transition = TransitionService.create_transition(narrative_map, from_block_id, to_block_id, note)  # RG028
        if transition is None:
            return None
        JourneySequenceService.recompute_all(narrative_map)  # RG044
        self.project_service.set_modified(True)
        return transition
