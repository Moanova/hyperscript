# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_project_service.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for project creation, save/load and model invariants (TSK07).

Covers:
- RG013/RG025/RG037/RG040: a new project has one map with a unique Start
  block, one default (and active) journey, and no orphan block
- RG061: the project is saved in a single JSON file with format_version
- FN005: the file path is application state, never serialized
- RG009/RG010/RG016: unsupported or foreign files are rejected, the current
  project is left unchanged
"""

import json

import pytest

from core.models.data_model import FORMAT_VERSION, Block
from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase


def test_create_project_initializes_map():
    service = ProjectService()
    project = CreateProjectUseCase(service).execute()

    assert project.lb == "New project"  # RG013
    assert service.current_project is project
    assert service.is_modified is False
    assert service.file_path is None  # unsaved project (RG003/FN005)

    assert len(project.narrative_maps) == 1
    nm = project.narrative_maps[0]
    assert nm.lb == "Main narrative map"  # RG013

    starts = [b for b in nm.block if b.typ == "Start"]
    assert len(starts) == 1  # RG025: unique, auto-created

    defaults = [j for j in nm.journey if j.default]
    assert len(defaults) == 1  # RG037/RG039: exactly one default journey
    assert nm.active_journey_id == defaults[0].id  # created and activated
    assert nm.get_active_journey() is defaults[0]

    # RG040: the Start block is attached to the default journey (no orphan block)
    assert any(jn.block_id == starts[0].id and jn.journey_id == defaults[0].id
               for jn in nm.journey_node)


def test_save_load_roundtrip(tmp_path):
    service = ProjectService()
    project = CreateProjectUseCase(service).execute()
    nm = project.narrative_maps[0]
    nm.block.append(Block(id=nm.get_next_id('block'), lb="Scene 1", typ="Scene"))

    path = tmp_path / "my_project.json"
    assert service.save_project(str(path))
    assert service.file_path == str(path)
    assert service.is_modified is False

    raw = json.loads(path.read_text(encoding='utf-8'))
    assert raw['format_version'] == FORMAT_VERSION  # RG010/RG061
    assert 'file_path' not in raw  # FN005: file path is not business data
    assert raw['narrative_maps'][0]['lb'] == "Main narrative map"

    other = ProjectService()
    assert other.load_project(str(path))
    loaded = other.current_project
    assert loaded.lb == project.lb
    assert [b.typ for b in loaded.narrative_maps[0].block] == ["Start", "Scene"]
    assert other.file_path == str(path)
    assert other.is_modified is False


def test_load_rejects_incompatible_file(tmp_path):
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    before = service.current_project

    # planoscript-like file: no format_version, old singular keys
    path = tmp_path / "old.json"
    path.write_text(json.dumps({"id": "x", "lb": "old", "narrative_map": []}), encoding='utf-8')

    assert service.load_project(str(path)) is False  # RG010/RG016
    assert service.current_project is before  # RG009: current project unchanged


def test_load_missing_file_keeps_current_project(tmp_path):
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    before = service.current_project
    assert service.load_project(str(tmp_path / "nope.json")) is False
    assert service.current_project is before


def test_block_condition_only_on_condition_type():
    # the structured condition is the sole carrier, only on Condition blocks
    Block(id=1, lb="c", typ="Condition", condition={"kind": "Choice", "lb": "has key"})
    with pytest.raises(ValueError):
        Block(id=2, lb="s", typ="Scene", condition={"kind": "Choice"})
    with pytest.raises(ValueError):
        Block(id=3, lb="x", typ="Nope")
    with pytest.raises(ValueError):
        Block(id=4, lb="c", typ="Condition", condition={"kind": "Nope"})
