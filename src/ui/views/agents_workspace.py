# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agents_workspace.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Agents workspace (TSK19b): the QGraphicsView of the "Agents" tab.

Dedicated workspace for project-level agents (RG057), re-designed session
04 (RG065/RG066/RG067) — the planoscript agents x blocks matrix is NOT
reused. Same dark background as the "Journeys" view, but dressed with
anchor dots instead of a grid (spacing/radius/color from config.json),
drawn in drawBackground over the visible area only (no scene items, so no
z-order trap). Each project agent is shown as an AgentCardItem (larger
than a block, no ports, no participation badge); cards are freely movable
but their position is always forced onto the nearest anchor dot (RG065).
Card positions are persisted at project level (layouts/project.json,
RG067).

The filters (journey/agent, RG048/RG063) do NOT apply to this view.

The workspace NEVER writes the business model (RG058): it emits signals
and the MainWindow applies the use cases.
"""
import logging

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene,
    QGraphicsItem,
    QFrame,
)
from PySide6.QtCore import Qt, QPointF, Signal, QObject, QEvent
from PySide6.QtGui import QColor, QBrush, QPainter

from core.models.view_model import ProjectLayout, AgentCardLayout
from core.services.layout_service import LayoutService
from ui.nodes.agent_card import AgentCardItem
from ui.utils import theme
from config.config_loader import get as _get_config

_BG_PRIMARY = _get_config("bg_primary", theme.BG_PRIMARY)
_DOT_SPACING = _get_config("agents_view_dot_spacing_px", 20)
_DOT_RADIUS = _get_config("agents_view_dot_radius_px", 1.5)
_DOT_COLOR = _get_config("agents_view_dot_color", "#4A4A4A")
_CARD_WIDTH = _get_config("agents_view_card_width", 160.0)
_CARD_HEIGHT = _get_config("agents_view_card_height", 100.0)

logger = logging.getLogger(__name__)

# Auto-scroll margin (px) from the viewport edges while dragging (04_interface)
_SCROLL_MARGIN = 50
_SCROLL_SPEED = 20


class AgentsWorkspace(QGraphicsView, QObject):
    """Workspace of the "Agents" view: one card per project agent."""

    # Emitted when the visual workspace changed (card moved - FN017/RG060)
    workspace_modified = Signal()

    # Emitted on right-click after selecting the item under the cursor (RG055):
    # MainWindow builds the context menu dynamically from the application menu
    context_menu_requested = Signal(object, object)  # item (AgentCardItem/None), global QPoint

    def __init__(self, project=None, info_bar=None, main_window=None):
        super().__init__()

        # No frame: the default QFrame StyledPanel border was drawn in
        # light gray (bottom-left corner above the info bar)
        self.setFrameShape(QFrame.NoFrame)

        self.project = project
        self.info_bar = info_bar
        self.main_window = main_window

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(QBrush(QColor(_BG_PRIMARY)))

        self.setStyleSheet(theme.WORKSPACE_STYLESHEET)
        # A plain QWidget subclass does not paint its stylesheet
        # background unless WA_StyledBackground is set
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Initial scene size 4000x4000 so the scrollbars are active by default
        self.scene_rect_margin = 200
        self.setSceneRect(0, 0, 4000, 4000)

        # Scrollbars always visible
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.centerOn(2000, 2000)

        # Anchor dots are painted in drawBackground over the visible area;
        # a repaint is enough to refresh them on scroll/resize
        self.horizontalScrollBar().valueChanged.connect(self.viewport().update)
        self.verticalScrollBar().valueChanged.connect(self.viewport().update)

        # No rubber band: single selection only (RG049)
        self.setDragMode(QGraphicsView.NoDrag)

        self.setRenderHint(QPainter.Antialiasing)

    # ------------------------------------------------------------------
    # Anchor dots / scene geometry
    # ------------------------------------------------------------------

    def drawBackground(self, painter, rect):
        """RG065: fill the background like the "Journeys" view (bg_primary)
        and draw the anchor dots over the visible area only (no scene
        items, so the dots can never overprint a card)."""
        super().drawBackground(painter, rect)
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(_DOT_COLOR)))
        start_x = int(rect.left() - (rect.left() % _DOT_SPACING))
        start_y = int(rect.top() - (rect.top() % _DOT_SPACING))
        for x in range(start_x, int(rect.right()) + int(_DOT_SPACING), int(_DOT_SPACING)):
            for y in range(start_y, int(rect.bottom()) + int(_DOT_SPACING), int(_DOT_SPACING)):
                painter.drawEllipse(QPointF(x, y), _DOT_RADIUS, _DOT_RADIUS)
        painter.restore()

    def resizeEvent(self, event):
        """Repaint the dots for the new visible area."""
        super().resizeEvent(event)
        self.viewport().update()

    def _expand_scene_to_include(self, x: float, y: float, margin: int = None):
        """Dynamically expand the sceneRect to include the point (x, y)."""
        if margin is None:
            margin = self.scene_rect_margin
        new_rect = self.sceneRect()
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
            self.setSceneRect(new_rect)

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

        # Auto-scroll when the mouse is near a viewport edge while dragging
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

        Item tooltips are shown instantly by the items themselves (see
        AgentCardItem.hoverEnterEvent). Letting the automatic mechanism run
        would pop a second tooltip at the cursor when the mouse rests.
        """
        if event.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(event)

    def mousePressEvent(self, event):
        """Single selection (RG049): a click on a card selects it alone, a
        click on the empty area deselects."""
        item = self._agent_card_at(event.position().toPoint())

        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            if item is None:
                self._clear_all_selections()
            elif item.flags() & QGraphicsItem.ItemIsSelectable:
                self._select_item_only(item)

    # ------------------------------------------------------------------
    # Cards
    # ------------------------------------------------------------------

    def _agent_card_at(self, view_pos):
        """Return the AgentCardItem under the view position, climbing to the
        parent card when a child (label, type) is hit."""
        item = self.itemAt(view_pos)
        if item is not None and not isinstance(item, AgentCardItem):
            parent = item.parentItem()
            item = parent if isinstance(parent, AgentCardItem) else None
        return item

    def find_agent_card(self, agent_id: int):
        """Find the AgentCardItem of a business agent id."""
        for item in self.scene.items():
            if isinstance(item, AgentCardItem) and item.entity.id == agent_id:
                return item
        return None

    def next_free_card_position(self, x: float = 80.0, y: float = 80.0):
        """First anchor-dot-snapped, non-overlapping position near (x, y)
        for a new card (RG050, on the dot grid)."""
        existing_rects = []
        for item in self.scene.items():
            if isinstance(item, AgentCardItem):
                r = item.rect()
                pos = item.pos()
                existing_rects.append((pos.x(), pos.y(), r.width(), r.height()))
        x, y = LayoutService.find_non_overlapping_position(
            LayoutService.snap_to_grid(x, grid_size=_DOT_SPACING),
            LayoutService.snap_to_grid(y, grid_size=_DOT_SPACING),
            _CARD_WIDTH, _CARD_HEIGHT, existing_rects)
        return (LayoutService.snap_to_grid(x, grid_size=_DOT_SPACING),
                LayoutService.snap_to_grid(y, grid_size=_DOT_SPACING))

    def create_agent_card(self, agent, layout: AgentCardLayout = None, select: bool = True,
                          skip_overlap_check: bool = False):
        """Create an AgentCardItem from the business agent and its layout.

        RG050: unless skip_overlap_check (loading saved positions), the
        position is adjusted to avoid overlapping an existing card.
        """
        if layout is None:
            x, y = self.next_free_card_position()
            layout = AgentCardLayout(agent_id=agent.id, x=x, y=y,
                                     width=_CARD_WIDTH, height=_CARD_HEIGHT)

        if not skip_overlap_check:
            existing_rects = []
            for item in self.scene.items():
                if isinstance(item, AgentCardItem):
                    r = item.rect()
                    pos = item.pos()
                    existing_rects.append((pos.x(), pos.y(), r.width(), r.height()))
            layout.x, layout.y = LayoutService.find_non_overlapping_position(
                layout.x, layout.y, layout.width, layout.height, existing_rects
            )
            layout.x = LayoutService.snap_to_grid(layout.x, grid_size=_DOT_SPACING)
            layout.y = LayoutService.snap_to_grid(layout.y, grid_size=_DOT_SPACING)

        card = AgentCardItem(agent, layout)
        self.add_item_at(layout.x, layout.y, card)
        card.register_position_observer(lambda c=card: self._on_card_moved(c))
        if select:
            self._select_item_only(card)
        return card

    def _on_card_moved(self, moved_card):
        """Notify the MainWindow (FN017: a move marks the project modified)."""
        self.workspace_modified.emit()

    def add_agent_card(self, agent, select: bool = True):
        """Add a card for a newly created agent (called by MainWindow after
        the use case, RG058)."""
        return self.create_agent_card(agent, select=select)

    def remove_agent_card(self, agent_id: int) -> bool:
        """Remove the card of a deleted agent."""
        card = self.find_agent_card(agent_id)
        if card is None:
            return False
        self.scene.removeItem(card)
        return True

    def refresh_agent_card(self, agent) -> None:
        """Refresh the card content after the agent was edited."""
        card = self.find_agent_card(agent.id)
        if card is not None:
            card.update_entity_data()

    def _select_item_only(self, item):
        """Select only the given item, deselect the others (RG049)."""
        for existing_item in self.scene.items():
            if (existing_item is not item
                    and existing_item.flags() & QGraphicsItem.ItemIsSelectable):
                existing_item.setSelected(False)
        if item.flags() & QGraphicsItem.ItemIsSelectable:
            item.setSelected(True)

    def _clear_all_selections(self):
        """Deselect every selectable item (RG049: a click on empty space)."""
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                item.setSelected(False)

    def get_selected_item(self):
        """Return the single selected AgentCardItem, or None."""
        selected = [i for i in self.scene.selectedItems()
                    if isinstance(i, AgentCardItem)]
        return selected[0] if selected else None

    # ------------------------------------------------------------------
    # Population and project-level layout persistence (RG067)
    # ------------------------------------------------------------------

    def populate_agents(self, project, project_layout: ProjectLayout = None) -> int:
        """Create one card per project agent; positions are taken from the
        saved project layout when available, otherwise a free anchor-dot
        position is found (RG050/RG065)."""
        card_count = 0
        for agent in project.agent:
            saved = project_layout.get_agent_card_layout(agent.id) if project_layout else None
            if saved is not None:
                layout = AgentCardLayout(
                    agent_id=agent.id,
                    x=LayoutService.snap_to_grid(saved.x, grid_size=_DOT_SPACING),
                    y=LayoutService.snap_to_grid(saved.y, grid_size=_DOT_SPACING),
                    width=saved.width, height=saved.height)
                self.create_agent_card(agent, layout, select=False, skip_overlap_check=True)
            else:
                self.create_agent_card(agent, select=False)
            card_count += 1
        self._clear_all_selections()
        return card_count

    def collect_project_layout(self) -> ProjectLayout:
        """Collect the current card positions for project-level persistence
        (RG067)."""
        layout = ProjectLayout()
        for item in self.scene.items():
            if isinstance(item, AgentCardItem):
                item.update_layout()
                layout.add_agent_card(item.layout)
        return layout

    # ------------------------------------------------------------------
    # Context menu (RG055): the MainWindow builds the menu dynamically from
    # the application menu; here we only select the item under the cursor
    # ------------------------------------------------------------------

    def _on_context_menu_requested(self, pos):
        """Select the item under the cursor (RG055), then ask the MainWindow
        to open the dynamically aligned context menu."""
        # customContextMenuRequested delivers view coordinates
        scene_pos = self.mapToScene(self.viewport().mapFrom(self, pos))
        item = self.scene.itemAt(scene_pos, self.transform())
        if item is not None and not isinstance(item, AgentCardItem):
            parent = item.parentItem()
            item = parent if isinstance(parent, AgentCardItem) else None

        if isinstance(item, AgentCardItem):
            self._select_item_only(item)
        else:
            self._clear_all_selections()

        self.context_menu_requested.emit(item, self.mapToGlobal(pos))
