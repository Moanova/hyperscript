# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_agents_workspace_offscreen.py
# Version      : 4
# Date         : 2026-11-18
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen Qt tests for the Agents workspace (TSK21 cell snap on release).

Regression tests for the drag behavior (TSK19b corrective + TSK21, RG065
session 05):
- the scene rect must be set on the SCENE (items constrain their moves
  with scene.sceneRect()); setting it only on the view left
  scene.sceneRect() at the items bounding rect, which pinned the cards;
- Qt recomputes each ItemPositionChange proposal from the last RETURNED
  position, so the card accumulates its free position and never gets
  stuck on slow drags;
- RG065 (TSK21): during a drag the card moves freely in 2D — NO corridor
  (the axis lock of session 04 is removed, diagonals are possible) and no
  live snap; on RELEASE the card snaps to the nearest cell of the
  invisible grid (CELL_WIDTH x CELL_HEIGHT, anchored on the scene origin),
  or to the nearest free cell when the target cell is occupied;
- TSK30 (session 10, replaces TSK22): a NEW card is placed on the FIRST free
  cell of the invisible grid scanned row by row from the top-left corner
  (0, 0); the workspace extends rightwards/downwards only (scene rect left/
  top clamped at 0);
- TSK23 (RG065): the RELEASE cell must lie within the bounding box of the
  OTHER cards expanded by one cell (the group grows by at most one cell per
  move); outside that ring or on an occupied cell, the card is pulled back
  to the nearest free allowed cell — a single card stays free anywhere;
- programmatic setPos outside a mouse drag stays exact (no snap);
- the selected card is raised above the others (never hidden behind a
  neighbour).

These tests need a working Qt (offscreen). They are skipped when Qt /
libGL is not available (e.g. sandbox without libGL).
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QGraphicsItem
    from PySide6.QtCore import Qt, QPoint, QPointF
    from PySide6.QtTest import QTest
    _app = QApplication.instance() or QApplication([])
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from ui.views.agents_workspace import AgentsWorkspace
from ui.nodes.agent_card import AgentCardItem


def make_workspace(n_agents: int) -> AgentsWorkspace:
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    project = service.current_project
    for i in range(n_agents):
        CreateAgentUseCase(service).execute(lb=f"A{i}")
    ws = AgentsWorkspace(project=project)
    ws.resize(1200, 700)
    ws.populate_agents(project, None)
    _app.processEvents()
    return ws


def cards_of(ws):
    return sorted((it for it in ws.scene.items() if isinstance(it, AgentCardItem)),
                  key=lambda c: c.entity.lb)


def drag(ws, card, dx, dy, steps=10):
    center = ws.mapFromScene(card.sceneBoundingRect().center())
    if not ws.viewport().rect().contains(center):
        ws.centerOn(card.sceneBoundingRect().center())
        _app.processEvents()
        center = ws.mapFromScene(card.sceneBoundingRect().center())
    QTest.mousePress(ws.viewport(), Qt.LeftButton, Qt.NoModifier, center)
    _app.processEvents()
    assert ws.scene.mouseGrabberItem() is card
    for i in range(1, steps + 1):
        QTest.mouseMove(ws.viewport(), center + QPoint(int(dx * i / steps), int(dy * i / steps)))
        _app.processEvents()
    QTest.mouseRelease(ws.viewport(), Qt.LeftButton, Qt.NoModifier, center + QPoint(dx, dy))
    _app.processEvents()


def assert_on_cell(card):
    assert card.pos().x() % AgentCardItem.CELL_WIDTH == 0, f"x={card.pos().x()} not on a cell"
    assert card.pos().y() % AgentCardItem.CELL_HEIGHT == 0, f"y={card.pos().y()} not on a cell"


def assert_no_overlap(cards):
    rects = [(c.pos().x(), c.pos().y(), c.rect().width(), c.rect().height()) for c in cards]
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            x1, y1, w1, h1 = rects[i]
            x2, y2, w2, h2 = rects[j]
            overlap = not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
            assert not overlap, f"cards {i} and {j} overlap"


def test_scene_rect_is_set_on_the_scene_not_only_the_view():
    ws = make_workspace(1)
    # regression: view.setSceneRect alone leaves scene.sceneRect() at the
    # items bounding rect, which pins the cards
    assert ws.scene.sceneRect().width() >= 4000.0
    assert ws.scene.sceneRect().height() >= 4000.0


def test_initial_placement_is_on_cells_and_non_overlapping():
    ws = make_workspace(3)
    cards = cards_of(ws)
    # TSK30 (2.1): first free cells scanned row by row from the top-left
    # corner (0, 0) -> a growing row on the first grid row
    assert [(c.pos().x(), c.pos().y()) for c in cards] == [
        (0.0, 0.0), (200.0, 0.0), (400.0, 0.0)]
    for c in cards:
        assert_on_cell(c)
    assert_no_overlap(cards)


def test_new_card_in_empty_workspace_uses_top_left_cell():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    project = service.current_project
    ws = AgentsWorkspace(project=project)
    ws.resize(1200, 700)
    CreateAgentUseCase(service).execute(lb="A0")
    agent = next(a for a in project.agent if a.lb == "A0")
    card = ws.add_agent_card(agent)
    _app.processEvents()
    assert card.pos() == QPointF(0.0, 0.0)


def test_new_card_uses_first_free_cell_from_top_left():
    """TSK30 (2.1): a newly created card lands on the first free cell scanned
    from the top-left corner, even if a cell was freed inside the group."""
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    project = service.current_project
    CreateAgentUseCase(service).execute(lb="A0")
    CreateAgentUseCase(service).execute(lb="A1")
    ws = AgentsWorkspace(project=project)
    ws.resize(1200, 700)
    ws.populate_agents(project, None)
    _app.processEvents()
    cards = cards_of(ws)  # A0 (0, 0), A1 (200, 0)
    drag(ws, cards[0], 400, 0)  # free (400, 0) -> cell (400, 0), allowed ring
    assert cards[0].pos() == QPointF(400.0, 0.0)
    CreateAgentUseCase(service).execute(lb="A2")
    agent = next(a for a in project.agent if a.lb == "A2")
    new_card = ws.add_agent_card(agent)
    _app.processEvents()
    # (0, 0) was freed by the drag -> the new card takes it back (row-major
    # scan from the top-left corner)
    assert new_card.pos() == QPointF(0.0, 0.0)
    assert_on_cell(new_card)
    assert_no_overlap(cards_of(ws))


def test_scene_expansion_never_goes_left_or_up_of_origin():
    """TSK30 (2.1): the workspace extends rightwards/downwards only - the
    scene rect left/top edges stay clamped at 0."""
    ws = make_workspace(1)
    ws._expand_scene_to_include(-500.0, -500.0)
    rect = ws.scene.sceneRect()
    assert rect.left() == 0.0 and rect.top() == 0.0
    ws._expand_scene_to_include(4500.0, 4600.0)
    rect = ws.scene.sceneRect()
    assert rect.right() >= 4500.0 and rect.bottom() >= 4600.0
    assert rect.left() == 0.0 and rect.top() == 0.0


def test_release_outside_the_group_ring_is_pulled_back():
    """TSK23/RG065: the release cell must lie within the bounding box of the
    other cards expanded by one cell; a far drag is pulled back to the
    nearest free allowed cell."""
    ws = make_workspace(2)  # A0 (0, 0), A1 (200, 0)
    a0, a1 = cards_of(ws)
    drag(ws, a1, 3000, 3000)  # far away
    # others = [A0 (0,0,160,100)] -> allowed x in [0, 360], y in [0, 240]
    # snapped (3200, 2940) is clamped to (200, 140), which is free
    assert a1.pos() == QPointF(200.0, 140.0)
    assert_on_cell(a1)
    assert_no_overlap(cards_of(ws))


def test_single_card_can_be_moved_anywhere():
    """TSK23 edge case: with a single card there is no bounding box of other
    cards, so the release stays free anywhere in the scene."""
    ws = make_workspace(1)
    card = cards_of(ws)[0]  # (0, 0)
    drag(ws, card, 1000, 840)  # free (1000, 840) -> cell (1000, 840), allowed
    assert card.pos() == QPointF(1000.0, 840.0)


def test_programmatic_setpos_stays_free_no_snap():
    """Outside a mouse drag, setPos applies exactly (the cell snap happens
    only on mouse release)."""
    ws = make_workspace(1)
    card = cards_of(ws)[0]
    card.setPos(137.0, 155.0)
    _app.processEvents()
    assert (card.pos().x(), card.pos().y()) == (137.0, 155.0)
    assert (card.layout.x, card.layout.y) == (137.0, 155.0)


def test_diagonal_drag_moves_both_axes_then_snaps_on_release():
    """RG065 (TSK21): no corridor lock — a diagonal drag moves the card on
    BOTH axes during the drag; on release the position snaps to the nearest
    cell of the invisible grid."""
    ws = make_workspace(1)
    card = cards_of(ws)[0]
    card.setPos(0.0, 0.0)  # programmatic: stays exact
    _app.processEvents()
    drag(ws, card, 150, 90)  # free position (150, 90) -> nearest cell (200, 140)
    assert card.pos() == QPointF(200.0, 140.0)
    assert (card.layout.x, card.layout.y) == (200.0, 140.0)
    assert_on_cell(card)


def test_release_on_occupied_cell_goes_to_nearest_free_cell():
    ws = make_workspace(2)
    cards = cards_of(ws)  # A0 at (0, 0), A1 at (200, 0)
    a0, a1 = cards
    # drag A1 onto A0's cell: release at free (10, 10) -> cell (0, 0)
    # occupied by A0 -> nearest free cell (0, 140)
    drag(ws, a1, -190, 10)
    assert a1.pos() == QPointF(0.0, 140.0)
    assert_no_overlap(cards)
    # a free target cell is taken as-is
    drag(ws, a1, 210, 10)  # free (210, 150) -> cell (200, 140), free
    assert a1.pos() == QPointF(200.0, 140.0)
    assert_no_overlap(cards)


def test_selected_card_is_raised_above_neighbours():
    ws = make_workspace(3)
    cards = cards_of(ws)
    drag(ws, cards[0], 200, 200)  # (0, 0) -> free (200, 200) -> cell (200, 140)
    assert cards[0].pos() == QPointF(200.0, 140.0)
    assert cards[0].zValue() == 1.0
    assert all(c.zValue() == 0.0 for c in cards[1:])


def test_collect_project_layout_reports_card_positions():
    ws = make_workspace(2)
    cards = cards_of(ws)
    drag(ws, cards[0], 150, 90)  # (0, 0) -> free (150, 90) -> cell (200, 140)
    assert_on_cell(cards[0])
    layout = ws.collect_project_layout()
    card_layout = layout.get_agent_card_layout(cards[0].entity.id)
    assert card_layout is not None
    assert (card_layout.x, card_layout.y) == (cards[0].pos().x(), cards[0].pos().y())
