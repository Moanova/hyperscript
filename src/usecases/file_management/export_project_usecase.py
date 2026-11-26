# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : export_project_usecase.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""TSK42 (SU007/FN013): export the project as a standalone HTML reading
document ("Files > Export Project...").

The export writes a folder named after the project inside the parent folder
chosen by the user: index.html (links to every journey page + agents page +
orphans), one journey-<id>.html page per journey (linear reading sequence
from the Start block, RG044), agents.html and a shared style.css. The
document is autonomous: relative links only, no server, no external
dependency - readable in a standard browser offline (SU007).

Read-only (RG058): the use case never modifies the model, never marks the
map nor the project as modified, and never changes the project file path.
"""
import logging
import os
import re
from typing import Optional

from core.services.preview_service import PreviewService, EXPORT_CSS
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)

_INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]')


def sanitize_folder_name(name: str) -> str:
    """Make a label usable as a folder name on Windows (`/\\:*?"<>|`)."""
    cleaned = _INVALID_FILENAME_CHARS.sub("_", name or "").strip().strip(".")
    return cleaned or "export"


class ExportProjectUseCase:
    """Use case exporting the project as a static HTML site (SU007/FN013, TSK42)."""
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def target_folder(self, parent_dir: str) -> Optional[str]:
        """Path of the export folder for the current project (no write)."""
        project = self.project_service.current_project
        if project is None or not parent_dir:
            return None
        return os.path.join(parent_dir, sanitize_folder_name(project.lb))

    def execute(self, parent_dir: str) -> Optional[str]:
        """Write the export folder under parent_dir; return its path, or None
        on error (missing project/map, unwritable folder, ...)."""
        project = self.project_service.current_project
        if project is None or not parent_dir:
            return None
        nm = project.narrative_maps[0] if project.narrative_maps else None
        if nm is None:
            return None
        folder = self.target_folder(parent_dir)
        try:
            os.makedirs(folder, exist_ok=True)
            self._write(folder, "style.css", EXPORT_CSS)
            self._write(folder, "index.html",
                        PreviewService.build_export_index_html(project, nm))
            self._write(folder, "agents.html",
                        PreviewService.build_export_agents_html(project))
            for j in nm.journey:
                self._write(folder, f"journey-{j.id}.html",
                            PreviewService.build_export_journey_html(project, nm, j))
        except OSError as e:
            logger.error("Export error: %s", e)
            return None
        return folder

    @staticmethod
    def _write(folder: str, name: str, content: str) -> None:
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write(content)
