# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : delete_transition_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.services.project_service import ProjectService
from core.services.transition_service import TransitionService
from core.services.journey_sequence_service import JourneySequenceService


class DeleteTransitionUseCase:
    """FN022: delete a transition. Journey membership is derived from the
    blocks (RG041), so no attachment is removed. The confirmation dialog is
    the UI's responsibility."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, transition_id: int) -> bool:
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        if not TransitionService.delete_transition(narrative_map, transition_id):
            return False
        JourneySequenceService.recompute_all(narrative_map)  # RG044
        self.project_service.set_modified(True)
        return True
