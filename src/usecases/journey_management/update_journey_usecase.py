# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : update_journey_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Journey
from core.services.project_service import ProjectService


class UpdateJourneyUseCase:
    """FN024: edit the editable attributes of a journey (label and note)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey, lb: Optional[str] = None, note: Optional[str] = None) -> Optional[Journey]:
        if not self.project_service.current_project:
            return None
        if lb is not None:
            journey.lb = lb
        if note is not None:
            journey.note = note if note.strip() else None
        self.project_service.set_modified(True)
        return journey
