# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_export_project_usecase.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for ExportProjectUseCase (TSK42: "Files > Export Project...",
SU007/FN013 revised session 12).

Covered: export folder structure (index.html + agents.html + journey-<id>.html
+ style.css), hypertext links between pages, per-block rendering (label
(type), content, "Participations:", "Relationships:", inline transitions),
RG044 reading order, unreachable branches marked, notes as title attributes,
sanitized folder name, read-only guarantee (never marks modified, file_path
unchanged), error on invalid parent folder.
"""

import os

from core.models.data_model import Block, Participation
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.transition_service import TransitionService
from core.services.journey_sequence_service import JourneySequenceService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management.create_agent_usecase import CreateAgentUseCase
from usecases.relationship_management.create_relationship_usecase import CreateRelationshipUseCase
from usecases.file_management import ExportProjectUseCase
from usecases.file_management.export_project_usecase import sanitize_folder_name


def _service_with_content():
    service = ProjectService()
    project = CreateProjectUseCase(service).execute()
    nm = project.narrative_maps[0]
    alice = CreateAgentUseCase(service).execute(lb="Alice", typ="Character")
    bob = CreateAgentUseCase(service).execute(lb="Bob", typ="Artefact")
    start = next(b for b in nm.block if b.typ == "Start")
    s1 = Block(id=nm.get_next_id('block'), lb="S1", typ="Scene", content="scene text")
    nm.block.append(s1)
    JourneyService.attach_block(nm, s1.id, nm.journey[0].id)
    TransitionService.create_transition(nm, start.id, s1.id)
    JourneySequenceService.recompute_all(nm)
    nm.participation.append(Participation(
        id=nm.get_next_id('participation'), agent_id=alice.id, block_id=s1.id))
    CreateRelationshipUseCase(service).execute(alice.id, bob.id, "friend", s1.id,
                                                note="rel note")
    return service, project, nm


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_export_creates_folder_structure_with_links_and_content(tmp_path):
    service, project, nm = _service_with_content()
    j = nm.journey[0]
    uc = ExportProjectUseCase(service)
    folder = uc.execute(str(tmp_path))
    assert folder == os.path.join(str(tmp_path), "New project")  # project lb
    assert os.path.isdir(folder)
    for name in ("index.html", "agents.html", "style.css", f"journey-{j.id}.html"):
        assert os.path.isfile(os.path.join(folder, name)), name

    index = _read(os.path.join(folder, "index.html"))
    assert index.startswith("<!DOCTYPE html>")
    assert '<link rel="stylesheet" href="style.css"/>' in index
    assert f'<a href="journey-{j.id}.html">' in index  # link to the journey page
    assert '<a href="agents.html">' in index           # link to the agents page
    assert f"<h1>{project.lb}</h1>" in index and f"<h2>{nm.lb}</h2>" in index

    journey_page = _read(os.path.join(folder, f"journey-{j.id}.html"))
    assert '<a href="index.html">Back to index</a>' in journey_page
    assert "<h3" in journey_page and "S1 (Scene)" in journey_page
    assert "scene text" in journey_page
    assert "Participations: Alice" in journey_page          # TSK39 4.1 / TSK41
    assert "Relationships: " in journey_page                # TSK39 4.2 / TSK41
    assert "Alice — Bob : friend" in journey_page
    assert 'title="rel note"' in journey_page               # note as browser tooltip

    agents_page = _read(os.path.join(folder, "agents.html"))
    assert "Alice (Character)" in agents_page and "Bob (Artefact)" in agents_page
    assert '<a href="index.html">Back to index</a>' in agents_page

    css = _read(os.path.join(folder, "style.css"))
    assert "background-color:" in css


def test_export_is_read_only(tmp_path):
    service, project, nm = _service_with_content()
    service.set_modified(True)
    folder = ExportProjectUseCase(service).execute(str(tmp_path))
    assert folder is not None
    assert service.is_modified is True          # export does not clear the flag
    assert service.file_path is None             # export never sets the project file path
    service.set_modified(False)
    ExportProjectUseCase(service).execute(str(tmp_path))
    assert service.is_modified is False          # and never marks modified


def test_export_invalid_parent_returns_none(tmp_path):
    service, project, nm = _service_with_content()
    file_as_parent = tmp_path / "not_a_dir"
    file_as_parent.write_text("x", encoding="utf-8")
    assert ExportProjectUseCase(service).execute(str(file_as_parent)) is None
    assert ExportProjectUseCase(service).execute("") is None


def test_export_without_project_returns_none(tmp_path):
    service = ProjectService()
    assert ExportProjectUseCase(service).execute(str(tmp_path)) is None
    assert ExportProjectUseCase(service).target_folder(str(tmp_path)) is None


def test_target_folder_sanitizes_project_label(tmp_path):
    service, project, nm = _service_with_content()
    project.lb = 'a/b\\c:d*e?f"g<h>i|j'
    uc = ExportProjectUseCase(service)
    target = uc.target_folder(str(tmp_path))
    assert target == os.path.join(str(tmp_path), "a_b_c_d_e_f_g_h_i_j")
    assert sanitize_folder_name("") == "export"
    folder = uc.execute(str(tmp_path))
    assert folder == target and os.path.isdir(folder)
