# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : base_workspace.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Shared base of the QGraphicsView workspaces (TSK47).

BaseGraphicsWorkspace factors the common view/scene setup of
JourneysWorkspace and AgentsWorkspace: no frame, custom context menu,
scene with the dark background, initial 4000x4000 scene rect, always-on
scrollbars, no rubber-band drag, antialiasing, scene-rect helpers,
ensure_visible/add_item_at, drag auto-scroll and the swallowing of Qt's
delayed automatic tooltip event (items show their tooltip instantly).

Subclasses provide _on_context_menu_requested (RG055) and may override
_on_scroll_changed (repaint hook: dots in the Agents view, grid in the
Journeys view) and _expand_scene_to_include (the Agents view clamps the
left/top edges at 0 - TSK30 2.1).
"""
import logging

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QFrame
from PySide6.QtCore import Qt, QPointF, Signal, QObject, QEvent
from PySide6.QtGui import QColor, QBrush, QPainter

from ui.utils import theme

logger = logging.getLogger(__name__)

# Auto-scroll margin (px) from the viewport edges while dragging (04_interface)
_SCROLL_MARGIN = 50
_SCROLL_SPEED = 20


class BaseGraphicsWorkspace(QGraphicsView, QObject):
    """Common base of the QGraphicsView workspaces (Journeys, Agents)."""

    # Emitted when the visual workspace changed (item moved - FN017/RG060)
    workspace_modified = Signal()

    # Emitted on right-click after selecting the item under the cursor (RG055):
    # MainWindow builds the context menu dynamically from the application menu
    context_menu_requested = Signal(object, object)  # item or None, global QPoint

    def _init_view(self, info_bar=None, main_window=None) -> None:
        """Common view/scene setup shared by the graphics workspaces."""
        # No frame: the default QFrame StyledPanel border was drawn in
        # light gray (bottom-left corner above the info bar)
        self.setFrameShape(QFrame.NoFrame)

        self.info_bar = info_bar
        self.main_window = main_window

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(QBrush(QColor(theme.BG_PRIMARY)))

        self.setStyleSheet(theme.WORKSPACE_STYLESHEET)
        # A plain QWidget subclass does not paint its stylesheet
        # background unless WA_StyledBackground is set
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Initial scene size 4000x4000 so the scrollbars are active by default.
        # Set on the SCENE (items read scene.sceneRect() to constrain their
        # moves) and mirrored on the view (scroll range)
        self.scene_rect_margin = 200
        self._set_scene_rect(0, 0, 4000, 4000)

        # Scrollbars always visible
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.centerOn(2000, 2000)

        # Repaint hook on scroll (dots / grid depending on the view)
        self.horizontalScrollBar().valueChanged.connect(self._on_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

        # No rubber band: single selection only (RG049)
        self.setDragMode(QGraphicsView.NoDrag)

        self.setRenderHint(QPainter.Antialiasing)

    def _on_scroll_changed(self, value) -> None:
        """Repaint hook on scrollbar change (overridden by the Journeys view
        to redraw the grid)."""
        self.viewport().update()

    def _on_context_menu_requested(self, pos) -> None:
        """RG055: select the item under the cursor, then emit
        context_menu_requested. Implemented by each workspace."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Scene geometry
    # ------------------------------------------------------------------

    def _set_scene_rect(self, x: float, y: float, w: float, h: float):
        """Set the scene rect on the scene (items constrain their moves with
        scene.sceneRect()) and mirror it on the view (scroll range)."""
        self.scene.setSceneRect(x, y, w, h)
        self.setSceneRect(x, y, w, h)

    def _expand_scene_to_include(self, x: float, y: float, margin: int = None):
        """Dynamically expand the sceneRect to include the point (x, y).
        The Agents view overrides this to clamp the left/top edges at 0
        (TSK30 2.1: the workspace extends rightwards/downwards only)."""
        if margin is None:
            margin = self.scene_rect_margin
        new_rect = self.scene.sceneRect()
        expanded = False
        if x - margin < new_rect.left():
            new_rect.setLeft(x - margin)
            expanded = True
        if x + margin > new_rect.right():
            new_rect.setRight(x + margin)
            expanded = True
        if y - margin < new_rect.top():
            new_rect.setTop(y - margin)
            expanded = True
        if y + margin > new_rect.bottom():
            new_rect.setBottom(y + margin)
            expanded = True
        if expanded:
            self._set_scene_rect(new_rect.x(), new_rect.y(),
                                 new_rect.width(), new_rect.height())

    def ensure_visible(self, x: float, y: float, margin: int = 200):
        """Center the view when (x, y) falls outside the visible area (RG051)."""
        viewport_rect = self.viewport().rect()
        viewport_pos = self.mapFromScene(QPointF(x, y))
        if not viewport_rect.contains(viewport_pos):
            self.centerOn(x, y)

    def add_item_at(self, x: float, y: float, item: QGraphicsItem):
        """Add an item to the scene and expand the scene if needed."""
        self.scene.addItem(item)
        item.setPos(x, y)
        self._expand_scene_to_include(x, y)
        self.ensure_visible(x, y)

    # ------------------------------------------------------------------
    # Mouse / viewport events
    # ------------------------------------------------------------------

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self._auto_scroll_on_drag(event)

    def _auto_scroll_on_drag(self, event) -> None:
        """Auto-scroll when the mouse is near a viewport edge while dragging,
        and expand the scene to include the dragged items."""
        if event.buttons() == Qt.LeftButton:
            viewport_rect = self.viewport().rect()
            mouse_viewport_pos = event.position().toPoint()

            if mouse_viewport_pos.x() < _SCROLL_MARGIN:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - _SCROLL_SPEED)
            elif mouse_viewport_pos.x() > viewport_rect.width() - _SCROLL_MARGIN:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + _SCROLL_SPEED)
            if mouse_viewport_pos.y() < _SCROLL_MARGIN:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - _SCROLL_SPEED)
            elif mouse_viewport_pos.y() > viewport_rect.height() - _SCROLL_MARGIN:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + _SCROLL_SPEED)

            for item in self.scene.selectedItems():
                if not (item.flags() & QGraphicsItem.ItemIsMovable):
                    continue
                item_pos = item.scenePos()
                self._expand_scene_to_include(item_pos.x(), item_pos.y())

    def viewportEvent(self, event):
        """Swallow Qt's delayed automatic tooltip event.

        Item tooltips are shown instantly by the items themselves. Letting
        the automatic mechanism run would pop a second tooltip at the cursor
        when the mouse rests.
        """
        if event.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(event)
