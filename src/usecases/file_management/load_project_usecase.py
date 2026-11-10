# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : load_project_usecase.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.services.project_service import ProjectService

class LoadProjectUseCase:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, file_path: str) -> bool:
        """Execute the project loading (RG009/RG010/RG016)."""
        return self.project_service.load_project(file_path)
