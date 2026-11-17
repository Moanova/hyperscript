# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_agents_workspace_offscreen.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen Qt tests for the Agents workspace (TSK19b corrective + corridors).

Regression tests for the drag behavior reported by TSC (session 04):
- the scene rect must be set on the SCENE (items constrain their moves
  with scene.sceneRect()); setting it only on the view left
  scene.sceneRect() at the items bounding rect, which pinned the cards;
- Qt recomputes each ItemPositionChange proposal from the last RETURNED
  position, so the card accumulates its unsnapped position and never gets
  stuck on slow drags;
- RG065 corridors (TSC session 04, magnetic snap removed): during a drag
  the card slides in a single horizontal or vertical corridor — the
  dominant axis is locked at drag start, the other coordinate stays at its
  drag-start value; no snapping at all, the position stays free;
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


def test_scene_rect_is_set_on_the_scene_not_only_the_view():
    ws = make_workspace(1)
    # regression: view.setSceneRect alone leaves scene.sceneRect() at the
    # items bounding rect, which pins the cards
    assert ws.scene.sceneRect().width() >= 4000.0
    assert ws.scene.sceneRect().height() >= 4000.0


def test_initial_placement_is_free_and_non_overlapping():
    ws = make_workspace(3)
    cards = cards_of(ws)
    assert (cards[0].pos().x(), cards[0].pos().y()) == (80.0, 80.0)
    rects = [(c.pos().x(), c.pos().y(), c.rect().width(), c.rect().height()) for c in cards]
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            x1, y1, w1, h1 = rects[i]
            x2, y2, w2, h2 = rects[j]
            overlap = not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
            assert not overlap, f"cards {i} and {j} overlap"


def test_programmatic_setpos_is_free_no_snap_no_lock():
    """Outside a mouse drag, setPos applies exactly (no magnetic snap)."""
    ws = make_workspace(1)
    card = cards_of(ws)[0]
    card._drag_start = None
    card.setPos(137.0, 155.0)
    _app.processEvents()
    assert (card.pos().x(), card.pos().y()) == (137.0, 155.0)
    assert (card.layout.x, card.layout.y) == (137.0, 155.0)


def test_item_change_projects_onto_the_locked_axis():
    """During a drag with axis 'x' locked, the y coordinate stays at its
    drag-start value; the x coordinate is free (no snap)."""
    ws = make_workspace(1)
    card = cards_of(ws)[0]  # at (80, 80)
    card._drag_start = QPointF(80.0, 80.0)
    card._lock_axis = 'x'
    card.setPos(217.0, 130.0)
    _app.processEvents()
    assert (card.pos().x(), card.pos().y()) == (217.0, 80.0)
    # now lock the other axis
    card._drag_start = QPointF(217.0, 80.0)
    card._lock_axis = 'y'
    card.setPos(250.0, 260.0)
    _app.processEvents()
    assert (card.pos().x(), card.pos().y()) == (217.0, 260.0)


def test_mouse_drag_locks_a_single_corridor():
    """Integration: a diagonal mouse drag moves the card along ONE axis
    only (the dominant one, locked at drag start); the other coordinate
    stays exactly at its drag-start value."""
    ws = make_workspace(1)
    card = cards_of(ws)[0]
    x0, y0 = card.pos().x(), card.pos().y()
    drag(ws, card, 150, 150)
    x, y = card.pos().x(), card.pos().y()
    assert (x == x0) != (y == y0), f"both axes moved (x={x}, y={y}) — no corridor lock"
    assert max(x - x0, y - y0) > AgentCardItem.AXIS_LOCK_THRESHOLD_PX, "card did not move"


def test_card_drag_works_on_both_axes():
    """Successive horizontal then vertical drags both move the card
    (release re-arms the corridor lock)."""
    ws = make_workspace(1)
    card = cards_of(ws)[0]
    x0, y0 = card.pos().x(), card.pos().y()
    drag(ws, card, 120, 0)
    assert card.pos().x() > x0 and card.pos().y() == y0
    x1, y1 = card.pos().x(), card.pos().y()
    drag(ws, card, 0, 100)
    assert card.pos().y() > y1 and card.pos().x() == x1


def test_selected_card_is_raised_above_neighbours():
    ws = make_workspace(3)
    cards = cards_of(ws)
    drag(ws, cards[0], 200, 0)  # dragged towards the neighbours
    assert cards[0].pos().x() > 80.0, "card did not move"
    assert cards[0].zValue() == 1.0
    assert all(c.zValue() == 0.0 for c in cards[1:])


def test_collect_project_layout_reports_card_positions():
    ws = make_workspace(2)
    cards = cards_of(ws)
    drag(ws, cards[0], 40, 60)
    layout = ws.collect_project_layout()
    card_layout = layout.get_agent_card_layout(cards[0].entity.id)
    assert card_layout is not None
    assert (card_layout.x, card_layout.y) == (cards[0].pos().x(), cards[0].pos().y())
