# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_block_drag_offscreen.py
# Version      : 1
# Date         : 2026-11-18
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen Qt tests for the Journeys block drag (TSK24, RG046).

RG046 (TSK24, TSC session 05): during a drag the block follows the mouse
FREELY — no live snap, no saccades (the free position is accumulated in
_free_pos and the scene limits still apply); on RELEASE the block snaps to
the nearest grid point (grid_minor_size), clamped to the scene. A
programmatic setPos outside a mouse drag stays free (no snap). Creation
remains grid-snapped (LayoutService.snap_to_grid / create_node_layout).

These tests need a working Qt (offscreen). They are skipped when Qt /
libGL is not available (e.g. sandbox without libGL).
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
    from PySide6.QtCore import Qt, QPoint, QPointF
    from PySide6.QtTest import QTest
    _app = QApplication.instance() or QApplication([])
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from core.models.data_model import Block
from core.models.view_model import NodeLayout, BlockType
from config.config_loader import get as _get_config
from ui.nodes.block_node import BlockNode

GRID = float(_get_config("grid_minor_size", 20))


def make_view_with_node(x: float = 100.0, y: float = 100.0):
    block = Block(id=1, lb="B1", typ="Scene")
    layout = NodeLayout(node_id=1, node_type=BlockType.SCENE, x=x, y=y)
    node = BlockNode(block, layout)
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 4000, 4000)
    scene.addItem(node)
    view = QGraphicsView(scene)
    view.resize(1200, 700)
    _app.processEvents()
    return view, node


def test_drag_is_free_then_snaps_on_release():
    """RG046/TSK24: while the mouse button is held, the block is at the free
    position (237, 193 — not on the 20 px grid); on release it snaps to the
    nearest grid point (240, 200)."""
    view, node = make_view_with_node(100.0, 100.0)
    center = view.mapFromScene(node.sceneBoundingRect().center())
    QTest.mousePress(view.viewport(), Qt.LeftButton, Qt.NoModifier, center)
    _app.processEvents()
    assert view.scene().mouseGrabberItem() is node
    QTest.mouseMove(view.viewport(), center + QPoint(137, 93))
    _app.processEvents()
    # during the drag: free position, no snap
    assert node.pos() == QPointF(237.0, 193.0)
    QTest.mouseRelease(view.viewport(), Qt.LeftButton, Qt.NoModifier, center + QPoint(137, 93))
    _app.processEvents()
    # on release: snapped to the nearest grid point
    assert node.pos() == QPointF(240.0, 200.0)
    assert (node.layout.x, node.layout.y) == (240.0, 200.0)


def test_programmatic_setpos_stays_free():
    """Outside a mouse drag, setPos applies exactly (the grid snap happens
    only on mouse release)."""
    view, node = make_view_with_node(100.0, 100.0)
    node.setPos(137.0, 155.0)
    _app.processEvents()
    assert node.pos() == QPointF(137.0, 155.0)
    assert (node.layout.x, node.layout.y) == (137.0, 155.0)


def test_release_snaps_to_nearest_grid_point_clamped_to_scene():
    """A release near the scene edge snaps to the grid but stays entirely
    within the scene."""
    view, node = make_view_with_node(30.0, 30.0)
    node.setPos(10.0, 10.0)  # free (no drag)
    _app.processEvents()
    center = view.mapFromScene(node.sceneBoundingRect().center())
    QTest.mousePress(view.viewport(), Qt.LeftButton, Qt.NoModifier, center)
    _app.processEvents()
    QTest.mouseMove(view.viewport(), center + QPoint(-25, -15))
    _app.processEvents()
    QTest.mouseRelease(view.viewport(), Qt.LeftButton, Qt.NoModifier, center + QPoint(-25, -15))
    _app.processEvents()
    # free position would be (-15, -5), clamped to the scene (0, 0) then snapped
    assert node.pos() == QPointF(0.0, 0.0)
    assert node.pos().x() % GRID == 0 and node.pos().y() % GRID == 0
