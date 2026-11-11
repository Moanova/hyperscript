# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : create_journey_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Journey
from core.services.project_service import ProjectService


class CreateJourneyUseCase:
    """FN023: create a journey of the current narrative map. The new journey
    gets a unique id and a default label, and is NOT activated - the active
    journey stays unchanged (SU005/FN023)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, lb: Optional[str] = None, note: Optional[str] = None) -> Optional[Journey]:
        if not self.project_service.current_project:
            return None
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        entity_id = narrative_map.get_next_id('journey')
        journey = Journey(
            id=entity_id,
            lb=(lb.strip() if isinstance(lb, str) and lb.strip() else f"Journey {entity_id}"),
            default=False,
            note=(note if note and note.strip() else None),
        )
        narrative_map.journey.append(journey)
        # FN023: the active journey is left unchanged
        self.project_service.set_modified(True)
        return journey
