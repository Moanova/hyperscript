# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : update_transition_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Transition
from core.services.project_service import ProjectService


class UpdateTransitionUseCase:
    """FN021: edit a transition's editable attribute (the note only - a
    transition carries no condition, the structured condition is carried by
    the Condition block, FN035)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, transition: Transition, note: Optional[str] = None) -> Transition:
        if note is not None:
            transition.note = note
        self.project_service.set_modified(True)
        return transition
