# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agents_workspace.py
# Version      : 4
# Date         : 2026-11-26
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
in 2D during a drag (no axis lock, no live snap — RG065); on RELEASE the
card snaps to the nearest cell of an invisible cell grid
(agents_view_cell_width x agents_view_cell_height, anchored on the scene
origin), or to the nearest free cell when the target cell is occupied
(see AgentCardItem); the visible dots stay purely decorative.
Card positions are persisted at project level (layouts/project.json,
RG067).

TSK30 (session 10 feedback): a new card is placed on the FIRST free cell of
the invisible grid scanned row by row from the top-left corner, and
the workspace extends rightwards/downwards only - the scene rect never
grows past its left/top origin (clamped at 0, so card moves are constrained
to the same area via scene.sceneRect()). TSK31 (1.1): the grid origin is
offset by the inter-card gutter (cell size - card size), so the first card
keeps the same margin to the top/left edges as between two cards.

The filters (journey/agent, RG048/RG063) do NOT apply to this view.

The workspace NEVER writes the business model (RG058): it emits signals
and the MainWindow applies the use cases.
"""
import logging

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QBrush

from core.models.view_model import ProjectLayout, AgentCardLayout
from core.services.layout_service import LayoutService
from ui.nodes.agent_card import AgentCardItem
from ui.views.base_workspace import BaseGraphicsWorkspace
from ui.utils import theme
from config.config_loader import get as _get_config

_BG_PRIMARY = _get_config("bg_primary", theme.BG_PRIMARY)
_DOT_SPACING = _get_config("agents_view_dot_spacing_px", 20)
_DOT_RADIUS = _get_config("agents_view_dot_radius_px", 1.5)
_DOT_COLOR = _get_config("agents_view_dot_color", "#4A4A4A")
_CARD_WIDTH = _get_config("agents_view_card_width", 160.0)
_CARD_HEIGHT = _get_config("agents_view_card_height", 100.0)
_CELL_WIDTH = _get_config("agents_view_cell_width", 200.0)
_CELL_HEIGHT = _get_config("agents_view_cell_height", 140.0)
# TSK31 (1.1): the invisible grid is offset by the inter-card gutter, so the
# first card keeps the same margin to the top/left edges as between two cards
_GRID_OFFSET_X = _CELL_WIDTH - _CARD_WIDTH
_GRID_OFFSET_Y = _CELL_HEIGHT - _CARD_HEIGHT

logger = logging.getLogger(__name__)


class AgentsWorkspace(BaseGraphicsWorkspace):
    """Workspace of the "Agents" view: one card per project agent.

    TSK47: the common view/scene setup, ensure_visible/add_item_at, the
    drag auto-scroll and the tooltip swallowing come from
    BaseGraphicsWorkspace; the anchor dots and the cell-grid snap stay here.
    """

    def __init__(self, project=None, info_bar=None, main_window=None):
        super().__init__()
        self.project = project
        # Common view/scene setup (scroll repaint hook = viewport().update(),
        # which refreshes the anchor dots drawn in drawBackground)
        self._init_view(info_bar=info_bar, main_window=main_window)

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
        """Dynamically expand the sceneRect to include the point (x, y).
        TSK30 (2.1): the workspace extends rightwards/downwards only - the
        left/top edges are clamped at 0 and never grow in negative coords."""
        if margin is None:
            margin = self.scene_rect_margin
        new_rect = self.scene.sceneRect()
        expanded = False
        clamped_left = max(0.0, x - margin)
        if clamped_left < new_rect.left():
            new_rect.setLeft(clamped_left)
            expanded = True
        if x + margin > new_rect.right():
            new_rect.setRight(x + margin)
            expanded = True
        clamped_top = max(0.0, y - margin)
        if clamped_top < new_rect.top():
            new_rect.setTop(clamped_top)
            expanded = True
        if y + margin > new_rect.bottom():
            new_rect.setBottom(y + margin)
            expanded = True
        if expanded:
            self._set_scene_rect(new_rect.x(), new_rect.y(),
                                 new_rect.width(), new_rect.height())

    # ------------------------------------------------------------------
    # Mouse / viewport events
    # ------------------------------------------------------------------

    # mouseMoveEvent (auto-scroll on drag) and viewportEvent (tooltip
    # swallowing) are inherited from BaseGraphicsWorkspace

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

    def next_free_card_position(self, x: float = None, y: float = None):
        """First free cell of the invisible grid for a new card (RG050
        non-overlapping, RG065 cells), scanned row by row from the top-left
        corner (TSK30 2.1); the grid origin carries the inter-card gutter
        margin (TSK31 1.1); the (x, y) anchor is only a fallback when no
        free cell is found."""
        if x is None:
            x = _GRID_OFFSET_X
        if y is None:
            y = _GRID_OFFSET_Y
        existing_rects = []
        for item in self.scene.items():
            if isinstance(item, AgentCardItem):
                r = item.rect()
                pos = item.pos()
                existing_rects.append((pos.x(), pos.y(), r.width(), r.height()))
        scene_rect = self.scene.sceneRect()
        return LayoutService.find_first_free_cell(
            x, y, _CARD_WIDTH, _CARD_HEIGHT,
            existing_rects, _CELL_WIDTH, _CELL_HEIGHT,
            bounds=(scene_rect.left(), scene_rect.top(), scene_rect.right(), scene_rect.bottom()))

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

        # RG065: every card position is an origin of the invisible cell grid
        # (also on load, so legacy free positions snap to the nearest cell);
        # TSK31: the grid is offset by the inter-card gutter (TSK31 1.1)
        layout.x = LayoutService.snap_to_grid(layout.x, _CELL_WIDTH, _GRID_OFFSET_X)
        layout.y = LayoutService.snap_to_grid(layout.y, _CELL_HEIGHT, _GRID_OFFSET_Y)

        if not skip_overlap_check:
            existing_rects = []
            for item in self.scene.items():
                if isinstance(item, AgentCardItem):
                    r = item.rect()
                    pos = item.pos()
                    existing_rects.append((pos.x(), pos.y(), r.width(), r.height()))
            scene_rect = self.scene.sceneRect()
            layout.x, layout.y = LayoutService.find_nearest_free_position(
                layout.x, layout.y, layout.width, layout.height, existing_rects,
                _CELL_WIDTH, _CELL_HEIGHT,
                bounds=(scene_rect.left(), scene_rect.top(), scene_rect.right(), scene_rect.bottom())
            )

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
        saved project layout when available, otherwise a free cell of the
        invisible grid is found (RG050/RG065)."""
        card_count = 0
        for agent in project.agent:
            saved = project_layout.get_agent_card_layout(agent.id) if project_layout else None
            if saved is not None:
                layout = AgentCardLayout(
                    agent_id=agent.id,
                    x=saved.x,
                    y=saved.y,
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
