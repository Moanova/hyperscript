# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : save_project_usecase.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.services.project_service import ProjectService

class SaveProjectUseCase:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, file_path: str) -> bool:
        """Execute the project save (RG011/RG012/RG061)."""
        return self.project_service.save_project(file_path)
