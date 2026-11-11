# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : activate_journey_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Journey
from core.services.project_service import ProjectService


class ActivateJourneyUseCase:
    """FN026: activate a journey - it becomes the active journey of the map
    (the filter FN029 applies to it and new blocks are attached to it, RG040)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey) -> Optional[Journey]:
        if not self.project_service.current_project:
            return None
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        if journey not in narrative_map.journey:
            return None
        narrative_map.active_journey_id = journey.id  # FN026
        self.project_service.set_modified(True)
        return journey
