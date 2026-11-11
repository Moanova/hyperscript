# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : duplicate_journey_usecase.py
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


class DuplicateJourneyUseCase:
    """FN025/RG043: duplicate a journey - distinct label ('{lb} (copy)', the
    application is unilingual English), new id, default=False, NOT activated
    (RG038). The attachments of the source journey's blocks are copied to the
    new journey."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey) -> Optional[Journey]:
        if not self.project_service.current_project:
            return None
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        if journey not in narrative_map.journey:
            return None
        copy = Journey(
            id=narrative_map.get_next_id('journey'),
            lb=f"{journey.lb} (copy)",
            default=False,  # RG039: the default journey is unique and unchanged
            note=journey.note,
        )
        narrative_map.journey.append(copy)
        # RG043: copy the block attachments of the source journey
        for jn in [n for n in narrative_map.journey_node if n.journey_id == journey.id]:
            JourneyService.attach_block(narrative_map, jn.block_id, copy.id)
        # RG038: the active journey is not modified by the duplication
        JourneySequenceService.recompute_all(narrative_map)  # RG044
        self.project_service.set_modified(True)
        return copy
