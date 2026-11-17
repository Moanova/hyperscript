# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_agents_workspace_offscreen.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen Qt tests for the Agents workspace (TSK19b corrective).

Regression tests for the drag anomaly reported by TSC (session 04):
- the scene rect must be set on the SCENE (items constrain their moves
  with scene.sceneRect()); setting it only on the view left
  scene.sceneRect() at the items bounding rect, which pinned the cards
  (vertical move impossible, horizontal limited to the current bbox);
- Qt recomputes each ItemPositionChange proposal from the last RETURNED
  (snapped) position, so the card accumulates its unsnapped position and
  never gets stuck on slow drags;
- the card always lands on an anchor dot (RG065);
- the selected card is raised above the others (never hidden behind a
  neighbour).

These tests need a working Qt (offscreen). They are skipped when Qt /
libGL is not available (e.g. sandbox without libGL).
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QGraphicsItem
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtTest import QTest
    _app = QApplication.instance() or QApplication([])
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from config.config_loader import get as _get_config
from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from ui.views.agents_workspace import AgentsWorkspace
from ui.nodes.agent_card import AgentCardItem

SNAP_X = float(_get_config("agents_view_snap_step_x_px", 200.0))
SNAP_Y = float(_get_config("agents_view_snap_step_y_px", 120.0))


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
    # the scene rect is set on the scene (and may have been expanded by the
    # margin when populating), not left at the items bounding rect
    assert ws.scene.sceneRect().width() >= 4000.0
    assert ws.scene.sceneRect().height() >= 4000.0


def test_card_drag_works_on_both_axes_and_snaps_to_the_major_grid():
    ws = make_workspace(1)
    card = cards_of(ws)[0]
    # initial placement on the invisible major grid (RG065)
    assert (card.pos().x(), card.pos().y()) == (SNAP_X, SNAP_Y)
    drag(ws, card, 0, int(SNAP_Y) + 40)  # vertical: past half a cell -> next row
    assert card.pos().y() > SNAP_Y, "vertical drag did not move the card"
    assert card.pos().y() % SNAP_Y == 0, "card not snapped to the major grid"
    y_after_v = card.pos().y()
    drag(ws, card, int(SNAP_X) + 40, 0)  # horizontal: past half a cell -> next column
    assert card.pos().x() > SNAP_X, "horizontal drag did not move the card"
    assert card.pos().y() == y_after_v
    assert card.pos().x() % SNAP_X == 0, "card not snapped to the major grid"


def test_card_drag_vertical_works_with_several_cards():
    ws = make_workspace(3)
    cards = cards_of(ws)
    # all cards placed on the invisible major grid, one cell apart, no overlap
    assert [c.pos().x() for c in cards] == [SNAP_X, 2 * SNAP_X, 3 * SNAP_X]
    assert all(c.pos().y() == SNAP_Y for c in cards)
    card = cards[1]  # middle card
    drag(ws, card, 0, int(SNAP_Y) + 40)
    assert card.pos().y() > SNAP_Y, f"vertical drag did not move the card (y={card.pos().y()})"
    assert card.pos().y() % SNAP_Y == 0


def test_selected_card_is_raised_above_neighbours():
    ws = make_workspace(3)
    cards = cards_of(ws)
    drag(ws, cards[0], int(SNAP_X), 0)  # dragged one major cell to the right
    assert cards[0].pos().x() == 2 * SNAP_X, "card did not land on the next major cell"
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
    assert card_layout.x % SNAP_X == 0 and card_layout.y % SNAP_Y == 0
