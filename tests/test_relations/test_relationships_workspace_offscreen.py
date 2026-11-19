# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_relationships_workspace_offscreen.py
# Version      : 2
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen Qt tests for the Relationships workspace (TSK27, rewritten TSK29:
custom graphics scene, closer to the planoscript Agent x State matrix).

These tests need a working Qt (offscreen). They are skipped when Qt / libGL
is not available (e.g. sandbox without libGL) - to validate on the dev
workstation, like the other offscreen suites.

Covers (RG069/RG070 revised session 09, mockup 04_interface section 6,
design note docs/conception/04_relationships_matrix-FR/EN.md):
- matrix is N x N (all agents, even without relationship), symmetric, empty
  disabled diagonal (no self-relationship, RG035); initial row AND column
  orders alphabetical (label, ties by id);
- square cells (`relationships_view_cell_size_px`); cell (A, B) shows the
  type of the pair's derived state at the anchor block (default: the Start
  block, RG068); changing the anchor block recomputes the matrix;
- left click on a clickable cell emits cell_clicked(row, col) - the object
  that opens the create/edit dialog (MainWindow);
- filters (RG048/RG063/RG064) dim and disable out-of-filter cells; with the
  agent filter active, uninvolved agents' header cards are dimmed and cells
  of a pair not involving the filtered agent are not clickable (RG069);
- dragging a header card and releasing it reorders ONLY its own axis (rows
  and columns independent, RG070), emits axis_order_changed(row, col) and
  both orders are persisted in ProjectLayout (project level, RG067).
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QPointF, QEvent
    from PySide6.QtGui import QMouseEvent
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from core.models.view_model import ProjectLayout
from core.services.project_service import ProjectService
from core.services.journey_sequence_service import JourneySequenceService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.view_management import CreateBlockUseCase, CreateTransitionUseCase
from usecases.relationship_management import CreateRelationshipUseCase
from ui.views.relationships_workspace import (
    RelationshipsWorkspace, _CELL_SIZE, _CELLS_LEFT, _CELLS_TOP, _CARD_OFF_X, _CARD_OFF_Y,
)


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


def test_initial_orders_alphabetical_and_square_cells(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    # all 3 agents displayed on both axes, initial order alphabetical (RG070)
    assert ws._row_order == [alpha.id, mid.id, zoo.id]
    assert ws._col_order == [alpha.id, mid.id, zoo.id]
    assert ws.agent_id_at_row(0) == alpha.id
    assert ws.agent_id_at_col(2) == zoo.id
    # N x N cells, square (relationships_view_cell_size_px)
    assert len(ws._cells) == 9
    cell = ws._cells[(0, 1)]
    assert cell.rect().width() == _CELL_SIZE - 4  # _CELL_MARGIN = 2
    assert cell.rect().height() == _CELL_SIZE - 4
    # diagonal disabled (no self-relationship, RG035)
    assert not ws._cells[(0, 0)].clickable
    assert not ws._cells[(0, 0)].isEnabled()


def test_cell_shows_derived_state_and_anchor_default_is_start(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    assert ws.get_anchor_block_id() == start.id  # RG068/RG069 default
    # at Start (rank 0) no relation yet -> empty cells
    assert ws._cells[(0, 2)].typ is None  # Alpha x Zoo
    # select S1 in the panel -> cell shows "friend"
    ws.set_anchor_block(s1.id)
    assert ws._cells[(0, 2)].typ == "friend"
    assert ws._cells[(2, 0)].typ == "friend"  # symmetric (RG035)


def test_cell_left_click_emits_cell_clicked(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.set_anchor_block(s1.id)
    ws.resize(900, 700)
    received = []
    ws.cell_clicked.connect(lambda r, c: received.append((r, c)))
    cell = ws._cells[(0, 2)]  # Alpha x Zoo, clickable
    center = QPointF(cell.pos().x() + cell.rect().width() / 2,
                     cell.pos().y() + cell.rect().height() / 2)
    view_pos = ws.view.mapFromScene(center)
    ev = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(view_pos), QPointF(view_pos),
                     Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                     Qt.KeyboardModifier.NoModifier)
    ws.view.mousePressEvent(ev)
    assert received == [(0, 2)]


def test_filters_dim_cells_and_uninvolved_agent_cards(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.set_anchor_block(s1.id)
    # agent filter on Mid -> the Alpha-Zoo pair does not involve Mid: the cell
    # is not clickable (creation forbidden for uninvolved agents, RG069) and
    # the uninvolved header cards are dimmed
    ws.set_agent_filter(mid.id)
    assert not ws._cells[(0, 2)].clickable
    assert ws._row_cards[mid.id].opacity() == 1.0
    assert ws._col_cards[alpha.id].opacity() < 1.0
    assert ws._row_cards[zoo.id].opacity() < 1.0
    ws.set_agent_filter(None)
    assert ws._cells[(0, 2)].clickable
    assert ws._row_cards[alpha.id].opacity() == 1.0


def test_header_card_release_reorders_only_its_own_axis(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    received = []
    ws.axis_order_changed.connect(lambda r, c: received.append((list(r), list(c))))
    # drag the ROW card of Alpha and drop it on row index 2
    card = ws._row_cards[alpha.id]
    drop = QPointF(_CARD_OFF_X + 10, _CELLS_TOP + 2 * _CELL_SIZE + _CARD_OFF_Y)
    ws._on_card_released(card, drop)
    assert ws._row_order == [mid.id, zoo.id, alpha.id]
    # columns are independent (RG070 revised session 09): untouched
    assert ws._col_order == [alpha.id, mid.id, zoo.id]
    assert received and received[-1] == ([mid.id, zoo.id, alpha.id], [alpha.id, mid.id, zoo.id])
    # both orders persisted at project level
    layout = ProjectLayout()
    ws.collect_project_layout(layout)
    assert layout.relationships_view_row_order == [mid.id, zoo.id, alpha.id]
    assert layout.relationships_view_column_order == [alpha.id, mid.id, zoo.id]


def test_saved_orders_restored_on_populate(qapp):
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    # move the COLUMN card of Alpha to column index 2, persist, re-populate
    card = ws._col_cards[alpha.id]
    drop = QPointF(_CELLS_LEFT + 2 * _CELL_SIZE + _CARD_OFF_X, _CARD_OFF_Y + 10)
    ws._on_card_released(card, drop)
    layout = ProjectLayout()
    ws.collect_project_layout(layout)
    ws2 = RelationshipsWorkspace(project=ws.project, narrative_map=nm)
    ws2.populate(ws.project, nm, layout)
    assert ws2._col_order == [mid.id, zoo.id, alpha.id]
    assert ws2._row_order == [alpha.id, mid.id, zoo.id]
