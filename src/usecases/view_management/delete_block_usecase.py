# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : delete_block_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional, Dict

from core.services.project_service import ProjectService
from core.services.transition_service import TransitionService
from core.services.journey_sequence_service import JourneySequenceService


class DeleteBlockUseCase:
    """FN018: delete a block. The deletion cascades to its transitions,
    participations, anchored relationships and journey attachments (RG023);
    the removed elements are returned for the information message. The Start
    block can never be deleted (RG025)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, block_id: int) -> Optional[Dict[str, list]]:
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        block = TransitionService.get_block(narrative_map, block_id)
        if block is None:
            return None
        if block.typ == "Start":
            raise ValueError("The Start block cannot be deleted")  # RG025
        removed = TransitionService.delete_block_cascade(narrative_map, block_id)  # RG023
        JourneySequenceService.recompute_all(narrative_map)  # RG044
        self.project_service.set_modified(True)
        return removed
