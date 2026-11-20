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

Covers (RG069/RG070 revised session 10 TSK32, mockup 04_interface section 6,
design note docs/conception/04_relationships_matrix-FR/EN.md):
- UPPER-TRIANGLE matrix (TSK32): N x N grid, rows and columns carry the same
  agents with a SINGLE shared order (initial alphabetical, label then id);
  only cells with row < col are active - exactly one active cell per agent
  pair; the diagonal (no self-relationship, RG035) and the lower triangle are
  dimmed and non-interactive;
- square cells (`relationships_view_cell_size_px`); an active cell shows the
  pair's derived state at the anchor block (default: the Start block, RG068)
  as a MatrixRelationshipCard (border #E06666 = Pivot/Condition color, label
  = type, tooltip = type + pair + anchor + note, RG054); changing the anchor
  block recomputes the matrix;
- NO left click on cells (TSK32): creation/edition/deletion only via the
  right-click context menu - context_menu_requested(row, col) on an active
  cell, agent_context_menu_requested(agent_id) on a header card (RG055);
- filters (RG048/RG063/RG064) dim and disable out-of-filter cells; with the
  agent filter active, uninvolved agents' header cards are dimmed and cells
  of a pair not involving the filtered agent are not clickable (RG069);
- dragging a header card and releasing it reorders the single shared order
  (rows AND columns follow together, RG070 revised TSK32), emits
  axis_order_changed(order) and the order is persisted in ProjectLayout
  (`relationships_view_agent_order`, project level, RG067);
- TSK30/TSK31 (session 10 feedback, unchanged): view anchored top-left
  (AlignLeft|AlignTop, scene >= 4000x4000 at origin, scrollbars always on, no
  minimum size); grid covers the whole visible area with non-interactive
  lines; hit-testing in scene coordinates (mapFromScene); dots at every cell
  center; separator after the agent filter; journey combo emits the chosen
  journey id (None = All journeys); hover tooltips do not raise.
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QFrame, QGraphicsSceneHoverEvent
    from PySide6.QtCore import Qt, QPoint, QPointF, QSize, QEvent
    from PySide6.QtGui import QMouseEvent, QContextMenuEvent, QColor
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
    _CARD_OFF_X, _CARD_OFF_Y, _PANEL_WIDTH, _SEPARATOR_HEIGHT, _DOT_COLOR,
)
from ui.widgets.filters_side_panel import FiltersSidePanel  # TSK33
from ui.nodes.matrix_relationship_card import MatrixRelationshipCard  # TSK32
from ui.utils import theme


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
    assert ws._order == [alpha.id, mid.id, zoo.id]  # TSK32: single shared order
    assert ws._row_order == ws._col_order == ws._order
    assert ws.agent_id_at_row(0) == alpha.id
    assert ws.agent_id_at_col(2) == zoo.id
    # N x N cells, square (relationships_view_cell_size_px)
    assert len(ws._cells) == 9
    cell = ws._cells[(0, 1)]
    assert cell.rect().width() == _CELL_SIZE - 4  # _CELL_MARGIN = 2
    assert cell.rect().height() == _CELL_SIZE - 4
    # TSK32: diagonal and lower triangle inactive; only row < col is active
    assert not ws._cells[(0, 0)].clickable      # diagonal (no self-relationship, RG035)
    assert not ws._cells[(0, 0)].isEnabled()
    assert not ws._cells[(1, 0)].clickable      # lower triangle
    assert ws._cells[(0, 1)].clickable          # upper triangle


def test_cell_hosts_relationship_card_in_the_single_active_cell(qapp):
    """TSK32: at anchor S1 the Alpha-Zoo pair has a "friend" relationship ->
    exactly ONE active cell (0, 2) hosts a MatrixRelationshipCard; the
    symmetric cell (2, 0) is in the lower triangle: no card, inactive."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    assert ws.get_anchor_block_id() == start.id  # RG068/RG069 default
    # at Start (rank 0) no relation yet -> no card
    assert ws._cells[(0, 2)].card is None  # Alpha x Zoo
    # select S1 in the panel -> the active cell hosts the card
    ws.set_anchor_block(s1.id)
    card = ws._cells[(0, 2)].card
    assert isinstance(card, MatrixRelationshipCard)
    assert card.rel_id is not None and card._label == "friend"
    # lower triangle: no card, not clickable (one active cell per pair, TSK32)
    assert ws._cells[(2, 0)].card is None
    assert not ws._cells[(2, 0)].clickable


def test_cell_left_click_does_nothing(qapp):
    """TSK32: no left-click action on the cells (creation/edition only via the
    right-click context menu, RG055) - a left click on an active cell emits
    no context-menu request and the cell_clicked signal no longer exists."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.set_anchor_block(s1.id)
    ws.resize(900, 700)
    received = []
    ws.context_menu_requested.connect(lambda r, c, g: received.append((r, c)))
    assert not hasattr(ws, "cell_clicked")
    cell = ws._cells[(0, 2)]  # Alpha x Zoo, active (upper triangle)
    center = QPointF(cell.pos().x() + cell.rect().width() / 2,
                     cell.pos().y() + cell.rect().height() / 2)
    view_pos = ws.view.mapFromScene(center)
    ev = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(view_pos), QPointF(view_pos),
                     Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                     Qt.KeyboardModifier.NoModifier)
    ws.view.mousePressEvent(ev)  # must not raise nor emit
    assert received == []


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


def test_header_card_release_reorders_the_single_shared_order(qapp):
    """TSK32: dragging a header card reorders the single shared order - the
    row AND the column axes follow together (RG070 revised); one list is
    emitted and persisted at project level."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    received = []
    ws.axis_order_changed.connect(lambda order: received.append(list(order)))
    # drag the ROW card of Alpha and drop it on row index 2
    card = ws._row_cards[alpha.id]
    drop = QPointF(_CARD_OFF_X + 10, _CELLS_TOP + 2 * _CELL_SIZE + _CARD_OFF_Y)
    ws._on_card_released(card, drop)
    assert ws._order == [mid.id, zoo.id, alpha.id]
    assert ws._row_order == ws._col_order == [mid.id, zoo.id, alpha.id]  # shared
    assert received and received[-1] == [mid.id, zoo.id, alpha.id]
    # the single order is persisted at project level
    layout = ProjectLayout()
    ws.collect_project_layout(layout)
    assert layout.relationships_view_agent_order == [mid.id, zoo.id, alpha.id]


def test_saved_shared_order_restored_on_populate(qapp):
    """TSK32: the single shared order is restored on populate (RG070 revised)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    # move the COLUMN card of Alpha to column index 2, persist, re-populate
    card = ws._col_cards[alpha.id]
    drop = QPointF(_CELLS_LEFT + 2 * _CELL_SIZE + _CARD_OFF_X, _CARD_OFF_Y + 10)
    ws._on_card_released(card, drop)
    layout = ProjectLayout()
    ws.collect_project_layout(layout)
    ws2 = RelationshipsWorkspace(project=ws.project, narrative_map=nm)
    ws2.populate(ws.project, nm, layout)
    assert ws2._order == [mid.id, zoo.id, alpha.id]
    assert ws2._row_order == ws2._col_order == [mid.id, zoo.id, alpha.id]


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


def test_real_mouse_drag_reorders_the_shared_order(qapp):
    """TSK30 (3.5) + TSK32: full press/move/release through the view handlers
    reorders the single shared order (rows and columns follow together)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(900, 700)
    received = []
    ws.axis_order_changed.connect(lambda order: received.append(list(order)))
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
    assert ws._order == [mid.id, zoo.id, alpha.id]
    assert ws._row_order == ws._col_order == [mid.id, zoo.id, alpha.id]  # shared (TSK32)
    assert received and received[-1] == [mid.id, zoo.id, alpha.id]


def test_relationship_card_tooltip_shows_type_pair_anchor(qapp):
    """TSK32 + RG054: the card in the active cell shows the full details in its
    tooltip on hover: type + agent pair + anchor block (+ note)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.set_anchor_block(s1.id)  # Alpha x Zoo = "friend" at S1
    card = ws._cells[(0, 2)].card
    assert card is not None
    tip = card.toolTip()
    assert "friend" in tip and "Alpha" in tip and "Zoo" in tip and "S1" in tip


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


def test_side_panel_has_thick_separator_after_agent_filter(qapp):
    """TSK30 (3.8) + TSK31 (3.1): a clearly visible filled separator bar
    separates the filter zone from the ordered block list."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    separators = [f for f in ws.findChildren(QFrame)
                  if f.minimumHeight() == f.maximumHeight() == _SEPARATOR_HEIGHT
                  and "background-color" in f.styleSheet()]
    assert separators
    assert _SEPARATOR_HEIGHT >= 2  # thicker than the old 1 px HLine


def test_matrix_card_hover_tooltip_does_not_raise(qapp):
    """TSK30 (3.4): hoverEnterEvent shows the tooltip immediately, without the
    invalid widget argument (a QGraphicsItem is not a QWidget)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    card = ws._row_cards[alpha.id]
    ev = QGraphicsSceneHoverEvent()
    ev.setScreenPos(QPoint(100, 100))
    card.hoverEnterEvent(ev)  # must not raise TypeError
    card.hoverLeaveEvent(ev)


# ---------------------------------------------------------------------
# TSK31 (session 10, 2nd feedback batch)
# ---------------------------------------------------------------------

def test_context_menu_event_on_cell_uses_pos_not_position(qapp):
    """TSK31 (2.1): right click on a cell - QContextMenuEvent exposes
    pos()/globalPos(), not position(); the context menu request is emitted."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(900, 700)
    received = []
    ws.context_menu_requested.connect(lambda r, c, g: received.append((r, c)))
    cell = ws._cells[(0, 1)]
    view_pos = ws.view.mapFromScene(cell.sceneBoundingRect().center())
    ev = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, view_pos,
                           ws.view.viewport().mapToGlobal(view_pos))
    ws.view.contextMenuEvent(ev)  # must not raise AttributeError
    assert received == [(0, 1)]


def test_diagonal_and_lower_triangle_dimmed_and_inactive(qapp):
    """TSK32 (upper triangle): cells with row >= col (diagonal + lower
    triangle) are dimmed and non-interactive; only row < col cells are active."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    # move the COLUMN card of Alpha to column index 2 -> shared order [mid, zoo, alpha]
    ws._on_card_released(ws._col_cards[alpha.id],
                         QPointF(_CELLS_LEFT + 2 * _CELL_SIZE + _CARD_OFF_X, _CARD_OFF_Y + 10))
    assert ws._order == [mid.id, zoo.id, alpha.id]
    # diagonal cell (0, 0) = mid x mid -> dimmed, inactive (no self-relationship, RG035)
    assert ws._cells[(0, 0)].dimmed is True
    assert ws._cells[(0, 0)].clickable is False
    # lower triangle (2, 0) = alpha x mid -> dimmed, inactive
    assert ws._cells[(2, 0)].dimmed is True
    assert ws._cells[(2, 0)].clickable is False
    # upper triangle (0, 2) = mid x alpha -> active
    assert ws._cells[(0, 2)].clickable is True
    assert ws._cells[(0, 2)].dimmed is False


def test_context_menu_on_header_card_emits_agent_id(qapp):
    """TSK32 + RG055: right click on an agent header card emits
    agent_context_menu_requested(agent_id, global pos)."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(900, 700)
    received = []
    ws.agent_context_menu_requested.connect(lambda aid, g: received.append(aid))
    card = ws._row_cards[alpha.id]
    view_pos = ws.view.mapFromScene(card.sceneBoundingRect().center())
    ev = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, view_pos,
                           ws.view.viewport().mapToGlobal(view_pos))
    ws.view.contextMenuEvent(ev)
    assert received == [alpha.id]


def test_context_menu_not_emitted_on_lower_triangle_cell(qapp):
    """TSK32: right click on an inactive (lower triangle) cell emits nothing."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(900, 700)
    received = []
    ws.context_menu_requested.connect(lambda r, c, g: received.append((r, c)))
    cell = ws._cells[(2, 0)]  # lower triangle: inactive
    view_pos = ws.view.mapFromScene(cell.sceneBoundingRect().center())
    ev = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, view_pos,
                           ws.view.viewport().mapToGlobal(view_pos))
    ws.view.contextMenuEvent(ev)
    assert received == []


def test_relationship_card_rendered_with_pivot_border_color(qapp):
    """TSK32: the card in the active cell is rendered with the #E06666
    (Pivot/Condition) border - pixel check on the card edges."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.set_anchor_block(s1.id)  # Alpha x Zoo = "friend" at S1 -> card in cell (0, 2)
    ws.resize(900, 700)
    ws.show()
    qapp.processEvents()
    img = ws.view.grab().toImage()
    card = ws._cells[(0, 2)].card
    assert card is not None
    # painted rect = mapToScene(0,0) + card size (sceneBoundingRect includes
    # the enlarged hit area of boundingRect, RG053)
    tl = card.mapToScene(0, 0)
    w, h = MatrixRelationshipCard.WIDTH, MatrixRelationshipCard.HEIGHT
    cx, cy = tl.x() + w / 2, tl.y() + h / 2
    samples = [QPointF(tl.x() + 1, cy), QPointF(tl.x() + w - 1, cy),
               QPointF(cx, tl.y() + 1), QPointF(cx, tl.y() + h - 1)]
    colors = {img.pixelColor(ws.view.mapFromScene(p)).name() for p in samples}
    assert "#e06666" in colors  # the Pivot/Condition border color
    # the card fill is the surface color, not the scene background
    assert img.pixelColor(ws.view.mapFromScene(QPointF(cx, cy))).name() == "#2d2d2d"
    ws.hide()


def test_dots_painted_over_the_whole_visible_area(qapp):
    """TSK31 (2.4): a dot at the center of every workspace cell, inside the
    matrix AND outside it (drawBackground), agents-view rendering."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(1200, 800)
    ws.show()
    qapp.processEvents()
    img = ws.view.grab().toImage()
    dot = QColor(_DOT_COLOR).name()
    for scene_pt in (QPointF(250, 150),   # inside the matrix (cell 1,0)
                     QPointF(650, 350),   # outside the matrix (cell 5,3)
                     QPointF(850, 650)):  # far corner of the visible area (outside the matrix)
        p = ws.view.mapFromScene(scene_pt)
        assert img.pixelColor(p).name() == dot, f"no dot at scene {scene_pt}"
    ws.hide()


def test_view_scrollbars_styled_like_journeys_view(qapp):
    """TSK31 (2.5): the matrix view scrollbars use the workspace theme
    (same appearance as the "Journeys" view) and are always on."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    assert "QScrollBar" in ws.view.styleSheet()
    assert ws.view.styleSheet() == theme.WORKSPACE_STYLESHEET
    assert ws.view.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOn
    assert ws.view.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOn


def test_no_gray_strip_on_the_right_of_the_panel(qapp):
    """TSK31 (3.2): the panel splitter slot is pinned to the panel width on
    resize - no exposed (light) splitter background on the right edge."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    ws.resize(1100, 700)
    ws.show()
    qapp.processEvents()
    sp = ws._splitter
    sizes = sp.sizes()
    assert sizes[-1] == _PANEL_WIDTH
    panel = next(c for c in sp.children()
                 if c.isWidgetType() and isinstance(c, FiltersSidePanel))  # TSK33
    assert panel.x() + panel.width() == sp.width()  # panel flush to the right edge
    ws.hide()


def test_block_list_scrollbar_always_on_and_dark(qapp):
    """TSK31 (3.2): the block list has an always-visible vertical scrollbar,
    styled like the Journeys scrollbars; it lives in the list zone only."""
    ws, nm, start, s1, alpha, zoo, mid = make_workspace(qapp)
    assert ws.block_list.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOn
    assert ws.block_list.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    assert "QScrollBar" in ws.block_list.styleSheet() or "QScrollBar" in theme.SIDE_PANEL_STYLESHEET
