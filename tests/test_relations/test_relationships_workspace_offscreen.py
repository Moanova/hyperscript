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
  both orders are persisted in ProjectLayout (project level, RG067);
- TSK30 (session 10 feedback): view anchored top-left (AlignLeft|AlignTop,
  scene >= 4000x4000 at origin, scrollbars always on, no minimum size);
  grid covers the whole visible area with non-interactive lines; hit-testing
  in scene coordinates (mapFromScene) so card drags and cell clicks work;
  cell checkbox with the type in the tooltip; separator after the agent
  filter; journey combo emits the chosen journey id (None = All journeys);
  MatrixAgentCard hover tooltip does not raise (QToolTip without widget arg).
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QFrame, QGraphicsSceneHoverEvent
    from PySide6.QtCore import Qt, QPoint, QPointF, QSize, QEvent
    from PySide6.QtGui import QMouseEvent
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from core.models.view_model import ProjectLayout
from core.services.project_service import ProjectService
from core.services.journey_sequence_service import JourneySequenceService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.journey_management import CreateJourneyUseCase
from usecases.view_management import CreateBlockUseCase, CreateTransitionUseCase
from usecases.relationship_management import CreateRelationshipUseCase
from ui.views.relationships_workspace import (
    RelationshipsWorkspace, _GridLineItem, _CELL_SIZE, _CELLS_LEFT, _CELLS_TOP,
    _CARD_OFF_X, _CARD_OFF_Y,
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


# ---------------------------------------------------------------------
# TSK30 (session 10 feedback)
# ---------------------------------------------------------------------

def test_view_anchored_top_left_with_always_on_scrollbars(qapp):
    """TSK30 (3.1/3.3/5): AlignLeft|AlignTop, no minimum size (the window can
    shrink), scrollbars always on."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    assert ws.view.alignment() == (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    assert ws.view.minimumSize() == QSize(0, 0)
    assert ws.view.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOn
    assert ws.view.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOn


def test_scene_rect_at_origin_and_at_least_4000(qapp):
    """TSK30 (3.1): scene anchored on the top-left corner, >= 4000x4000 so the
    scrollbars stay usable; grows rightwards/downwards only."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    r = ws.scene.sceneRect()
    assert r.left() == 0.0 and r.top() == 0.0
    assert r.width() >= 4000.0 and r.height() >= 4000.0


def test_grid_covers_the_whole_visible_area(qapp):
    """TSK30 (3.6): grid lines span the full visible rect (beyond the matrix
    bounds) and are non-interactive (_GridLineItem, empty shape)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(1200, 800)
    ws._draw_grid()
    lines = [it for it in ws.scene.items() if getattr(it, '_is_grid_line', False)]
    assert lines
    assert all(isinstance(l, _GridLineItem) for l in lines)
    assert all(l.shape().isEmpty() for l in lines)
    rect = ws.view.mapToScene(ws.view.viewport().rect()).boundingRect()
    vlines = [l for l in lines if l.line().x1() == l.line().x2()]
    hlines = [l for l in lines if l.line().y1() == l.line().y2()]
    # matrix width with 3 agents = 100 + 3*100 + 100 = 500: lines go beyond it
    assert any(l.line().x1() > 500.0 for l in vlines)
    assert any(l.line().y1() <= rect.top() and l.line().y2() >= rect.bottom() for l in vlines)
    assert any(l.line().x1() <= rect.left() and l.line().x2() >= rect.right() for l in hlines)


def test_card_and_cell_hit_testing_in_scene_coordinates(qapp):
    """TSK30 (3.5): _card_at/_cell_at map the scene position to item-local
    coordinates (shape() is local, items are positioned with setPos)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    card = ws._row_cards[zoo.id]  # last row card, far from the scene origin
    assert ws._card_at(card.sceneBoundingRect().center()) is card
    cell = ws._cells[(2, 1)]
    assert ws._cell_at(cell.sceneBoundingRect().center()) is cell
    assert ws._card_at(QPointF(5, 5)) is None
    assert ws._cell_at(QPointF(5, 5)) is None


def test_real_mouse_drag_reorders_only_its_own_axis(qapp):
    """TSK30 (3.5): full press/move/release through the view handlers reorders
    only the dragged card's axis (RG070)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(900, 700)
    received = []
    ws.axis_order_changed.connect(lambda r, c: received.append((list(r), list(c))))
    card = ws._row_cards[alpha.id]
    press_view = ws.view.mapFromScene(card.sceneBoundingRect().center())
    target_scene = QPointF(_CARD_OFF_X + 10, _CELLS_TOP + 2 * _CELL_SIZE + _CARD_OFF_Y)
    release_view = ws.view.mapFromScene(target_scene)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(press_view), QPointF(press_view),
                        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier)
    ws.view.mousePressEvent(press)
    assert ws.view._dragged_card is card
    move = QMouseEvent(QEvent.Type.MouseMove, QPointF(release_view), QPointF(release_view),
                       Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton,
                       Qt.KeyboardModifier.NoModifier)
    ws.view.mouseMoveEvent(move)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(release_view), QPointF(release_view),
                          Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
                          Qt.KeyboardModifier.NoModifier)
    ws.view.mouseReleaseEvent(release)
    assert ws._row_order == [mid.id, zoo.id, alpha.id]
    assert ws._col_order == [alpha.id, mid.id, zoo.id]  # untouched (RG070)
    assert received and received[-1] == ([mid.id, zoo.id, alpha.id], [alpha.id, mid.id, zoo.id])


def test_cell_tooltip_shows_relationship_type(qapp):
    """TSK30 (3.7): the relationship type shows in the cell tooltip on hover
    (the cell itself renders a checkbox with a filled gold circle)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.set_anchor_block(s1.id)  # Alpha x Zoo = "friend" at S1
    assert "friend" in ws._cells[(0, 2)].toolTip()


def test_journey_combo_emits_chosen_journey_id(qapp):
    """TSK30 (4.1): the side panel journey combo emits the chosen journey id
    (None = "All journeys") so the MainWindow can activate it."""
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    CreateJourneyUseCase(service).execute()  # second journey
    project = service.current_project
    nm = project.narrative_maps[0]
    ws = RelationshipsWorkspace(project=project, narrative_map=nm)
    ws.populate(project, nm, ProjectLayout())
    received = []
    ws.journey_filter_requested.connect(lambda jid: received.append(jid))
    j2 = nm.journey[-1]
    ws.journey_combo.setCurrentIndex(2)  # items: All journeys, j1, j2
    assert received[-1] == j2.id
    ws.journey_combo.setCurrentIndex(0)  # back to All journeys
    assert received[-1] is None


def test_side_panel_has_separator_after_agent_filter(qapp):
    """TSK30 (3.8): a horizontal separator separates the filter zone from the
    ordered block list."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    separators = [f for f in ws.findChildren(QFrame) if f.frameShape() == QFrame.Shape.HLine]
    assert separators


def test_matrix_card_hover_tooltip_does_not_raise(qapp):
    """TSK30 (3.4): hoverEnterEvent shows the tooltip immediately, without the
    invalid widget argument (a QGraphicsItem is not a QWidget)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    card = ws._row_cards[alpha.id]
    ev = QGraphicsSceneHoverEvent()
    ev.setScreenPos(QPoint(100, 100))
    card.hoverEnterEvent(ev)  # must not raise TypeError
    card.hoverLeaveEvent(ev)
