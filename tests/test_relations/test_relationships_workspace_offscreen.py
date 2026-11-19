# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_relationships_workspace_offscreen.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen Qt tests for the Relationships workspace (TSK27).

These tests need a working Qt (offscreen). They are skipped when Qt / libGL
is not available (e.g. sandbox without libGL) - to validate on the dev
workstation, like the other offscreen suites.

Covers (RG069/RG070, mockup 04_interface section 6):
- matrix is N x N (all agents, even without relationship), symmetric, empty
  diagonal, headers = agent labels, initial axis order alphabetical (label,
  ties by id);
- cell (A, B) shows the type of the pair's derived state at the anchor block
  (default: the Start block, RG068); changing the anchor block recomputes the
  matrix;
- filters (RG048/RG063/RG064) dim and disable out-of-filter cells;
- moving a header emits axis_order_changed with the new visual order and the
  order is persisted in ProjectLayout (RG070).
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from core.models.view_model import ProjectLayout
from core.services.project_service import ProjectService
from core.services.journey_sequence_service import JourneySequenceService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.view_management import CreateBlockUseCase, CreateTransitionUseCase
from usecases.relationship_management import CreateRelationshipUseCase
from ui.views.relationships_workspace import RelationshipsWorkspace


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def make_workspace(qapp):
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    project = service.current_project
    nm = project.narrative_maps[0]
    start = nm.block[0]
    s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
    CreateTransitionUseCase(service).execute(start.id, s1.id)
    JourneySequenceService.recompute_all(nm)  # RG044
    zoo = CreateAgentUseCase(service).execute(lb="Zoo")
    alpha = CreateAgentUseCase(service).execute(lb="Alpha")
    mid = CreateAgentUseCase(service).execute(lb="Mid")
    CreateRelationshipUseCase(service).execute(alpha.id, zoo.id, "friend", s1.id)
    ws = RelationshipsWorkspace(project=project, narrative_map=nm)
    ws.populate(project, nm, ProjectLayout())
    return ws, nm, start, s1, alpha, zoo, mid


def test_matrix_shape_headers_and_initial_order(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    # all 3 agents displayed, initial order alphabetical by label (RG070)
    assert ws._axis_order == [alpha.id, mid.id, zoo.id]
    assert ws.matrix.rowCount() == 3 and ws.matrix.columnCount() == 3
    assert ws.matrix.horizontalHeaderItem(0).text() == "Alpha"
    # diagonal disabled
    assert not (ws.matrix.item(0, 0).flags() & Qt.ItemIsEnabled)


def test_cell_shows_derived_state_and_anchor_default_is_start(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    assert ws.get_anchor_block_id() == start.id  # RG068/RG069 default
    # at Start (rank 0) no relation yet -> empty cells
    assert ws.matrix.item(0, 2).text() == ""  # Alpha x Zoo
    # select S1 in the panel -> cell shows "friend"
    ws.set_anchor_block(s1.id)
    assert ws.matrix.item(0, 2).text() == "friend"
    assert ws.matrix.item(2, 0).text() == "friend"  # symmetric (RG035)


def test_filters_dim_cells(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.set_anchor_block(s1.id)
    # agent filter on Mid -> the Alpha-Zoo pair does not involve Mid: the cell
    # is disabled (creation forbidden for uninvolved agents, RG069)
    ws.set_agent_filter(mid.id)
    assert not ws.matrix.item(0, 2).isEnabled()   # Alpha x Zoo: creation forbidden
    ws.set_agent_filter(None)
    assert ws.matrix.item(0, 2).isEnabled()


def test_header_move_emits_new_axis_order(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    received = []
    ws.axis_order_changed.connect(lambda order: received.append(list(order)))
    hh = ws.matrix.horizontalHeader()
    hh.moveSection(0, 2)  # Alpha to the end
    assert received and received[-1] == [mid.id, zoo.id, alpha.id]
    assert ws._axis_order == [mid.id, zoo.id, alpha.id]
    # persisted in the project layout (RG070)
    layout = ProjectLayout()
    ws.collect_project_layout(layout)
    assert layout.relationships_axis_order == [mid.id, zoo.id, alpha.id]
