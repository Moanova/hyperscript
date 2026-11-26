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
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService


class CreateJourneyUseCase:
    """FN023: create a journey of the current narrative map. The new journey
    gets a unique id and a default label, and is NOT activated - the active
    journey stays unchanged (SU005/FN023)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, lb: Optional[str] = None, note: Optional[str] = None) -> Optional[Journey]:
        """Create the journey; return it, or None when refused."""
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
        # RG068: the Start block is automatically attached to every new journey
        start = next((b for b in narrative_map.block if b.typ == "Start"), None)  # RG025
        if start is not None:
            JourneyService.attach_block(narrative_map, start.id, journey.id)
            JourneySequenceService.recompute_journey(narrative_map, journey.id)  # RG044
        # FN023: the active journey is left unchanged
        self.project_service.set_modified(True)
        return journey
