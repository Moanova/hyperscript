# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : project_service.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
import json
import logging
from datetime import datetime
from typing import Optional
from core.models.data_model import (
    FORMAT_VERSION,
    Project,
    NarrativeMap,
    new_project_id,
    new_narrative_map_id,
)

logger = logging.getLogger(__name__)


class ProjectService:
    """Holds the current project, its file path (application state, FN005) and the modified flag."""

    def __init__(self):
        self._current_project: Project = None
        self._file_path: str = None  # application state, not business data (FN005)
        self._is_modified = False
        # Optional observer hook: callable invoked on every set_modified(True).
        # Keeps core Qt-free: the UI layer registers a callback here and
        # re-emits it as a Qt signal.
        self.on_modified = None

    def create_project(self) -> Project:
        """Create a new unsaved project (RG003/RG013): named project with one empty narrative map."""
        narrative_map = NarrativeMap(
            id=new_narrative_map_id(),
            lb="Main narrative map",
        )
        self._current_project = Project(
            id=new_project_id(),
            lb="New project",
            narrative_maps=[narrative_map]
        )
        self._file_path = None
        self._is_modified = False
        return self._current_project

    def load_project(self, file_path: str) -> bool:
        """
        Load a project from a single JSON file (RG061).

        The file must carry the supported format_version (RG010); files from
        another application (e.g. planoscript) are rejected as incompatible
        (RG009/RG016) and the current project is left unchanged.

        Returns:
            bool: True if loading was successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_dict = json.load(f)
            if project_dict.get('format_version') != FORMAT_VERSION:
                logger.error("Unsupported or missing format_version in %s", file_path)
                return False
            self._current_project = Project.from_dict(project_dict)
            self._file_path = file_path
            self._is_modified = False
            return True
        except (IOError, OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            logger.error("Loading error: %s", e)
            return False

    def save_project(self, file_path: str) -> bool:
        """
        Save the current project to a single JSON file (RG061).

        The file path becomes the application state associated with the
        open project (FN005); the previous file is neither renamed nor
        deleted (RG012).

        Returns:
            bool: True if the save was successful
        """
        if not self._current_project:
            return False

        # Prepare the dict with updated metadata without mutating the project
        now = datetime.now()
        project_dict = self._current_project.to_dict()
        project_dict['modification_date_time'] = now.isoformat()

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_dict, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            logger.error("Saving error: %s", e)
            return False

        # Update metadata only after successful write
        self._current_project.modification_date_time = now
        self._file_path = file_path
        self._is_modified = False
        return True

    def close_project(self) -> None:
        """Close the current project: clear it from memory and reset the application state."""
        self._current_project = None
        self._file_path = None
        self._is_modified = False

    @property
    def current_project(self) -> Project:
        return self._current_project

    @property
    def file_path(self) -> Optional[str]:
        """File path of the open project (application state, not serialized - FN005)."""
        return self._file_path

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    def set_modified(self, modified: bool) -> None:
        self._is_modified = modified
        if modified and callable(self.on_modified):
            self.on_modified()
