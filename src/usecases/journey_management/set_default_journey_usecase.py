# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : set_default_journey_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Journey
from core.services.project_service import ProjectService


class SetDefaultJourneyUseCase:
    """FN038/RG062: designate a journey as the default journey of the map. The
    designation replaces the current default (there is always exactly one,
    RG039) and does NOT modify the active journey."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey) -> Optional[Journey]:
        if not self.project_service.current_project:
            return None
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        if journey not in narrative_map.journey:
            return None
        for j in narrative_map.journey:  # RG039/RG062: a single default journey
            j.default = (j is journey)
        # RG062: the active journey is not modified
        self.project_service.set_modified(True)
        return journey
