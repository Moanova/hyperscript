# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_file_usecases.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the file management use cases (TSK07).

Covers: save/load through the use cases (FN006/FN008/FN009), the quit
confirmation logic (FN002), and project closing (FN010).
"""

import json

from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.file_management import (
    LoadProjectUseCase, SaveProjectUseCase, QuitApplicationUseCase
)


def _new_project_service() -> ProjectService:
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def test_save_and_load_usecases(tmp_path):
    service = _new_project_service()
    path = str(tmp_path / "p.json")

    assert SaveProjectUseCase(service).execute(path)
    assert service.file_path == path
    assert service.is_modified is False

    other = ProjectService()
    assert LoadProjectUseCase(other).execute(path)
    assert other.current_project.lb == "New project"
    assert other.file_path == path


def test_quit_confirmation_only_when_modified():
    service = _new_project_service()
    quit_usecase = QuitApplicationUseCase(service)
    assert quit_usecase.should_ask_confirmation() is False  # FN002
    service.set_modified(True)
    assert quit_usecase.should_ask_confirmation() is True


def test_close_project_resets_application_state():
    service = _new_project_service()
    service.set_modified(True)
    service.close_project()  # FN010
    assert service.current_project is None
    assert service.file_path is None
    assert service.is_modified is False
