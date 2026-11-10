# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : quit_application_usecase.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.services.project_service import ProjectService

class QuitApplicationUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def should_ask_confirmation(self) -> bool:
        """Decide whether a save confirmation is required before quitting (FN002): pure logic."""
        return self.project_service.is_modified
