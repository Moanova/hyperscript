# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agent_card.py
# Version      : 4
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Agent card of the "Agents" view (TSK19b, RG065/RG066; TSK46: now a
BaseNode subclass - paint/shape/hover/drag/observers are inherited).

Visual representation of a project Agent (RG057), re-designed session 04:
a card larger than a narrative block (agents_view_card_width x
agents_view_card_height, config.json), WITHOUT ports and WITHOUT a
participation-count badge (participations/relationships are handled in
other views). The card shows the agent label and type; the note is shown
in an immediate hover tooltip (RG054).

The card is freely movable in 2D during a drag — no axis lock, no live
snap (RG065, TSC sessions 04/05: continuous snapping made the moves
awkward). On RELEASE, the card snaps to the nearest cell of an invisible
cell grid (CELL_WIDTH x CELL_HEIGHT from config, anchored on the scene
origin); the release cell must lie within the bounding box of the OTHER
cards expanded by one cell (TSK23 — a lone card stays free), and if the
cell is outside that ring or occupied, the card is placed on the nearest
free allowed cell. The position is also cell-snapped at creation and
load (AgentsWorkspace). The visible dots stay purely decorative. Single
selection (RG049), dashed selection outline in the card color (charter 98:
selection > hover > type), hit-testing via shape() (RG053).

The card accent color is the sand accent (block_scene_color, #E5C07B) —
TSC feedback session 04: the card outline is sand, not gold (the gold
#D19A66 was the initial choice, planoscript reference: agent cards used
the event tint copper).
"""

from typing import Any

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QFont

from core.models.data_model import Agent
from core.models.view_model import AgentCardLayout
from core.services.layout_service import LayoutService
from config.config_loader import get as _get_config
from ui.nodes.base_node import BaseNode
from ui.utils import theme


class AgentCardItem(BaseNode):
    """Visual representation of an Agent entity in the "Agents" workspace."""

    # Card dimensions (config.json, larger than a block 80x40)
    WIDTH = _get_config("agents_view_card_width", 160.0)
    HEIGHT = _get_config("agents_view_card_height", 100.0)
    # BaseNode fallback dimensions when the layout carries no size
    DEFAULT_WIDTH = WIDTH
    DEFAULT_HEIGHT = HEIGHT

    # Colors (dark theme via ui.utils.theme; no hard-coded values)
    CARD_BORDER_COLOR = theme.color("block_scene_color", theme.BLOCK_SCENE_COLOR)  # sand (TSC session 04)
    DEFAULT_BORDER_COLOR = CARD_BORDER_COLOR  # BaseNode appearance uses this
    TEXT_COLOR = theme.color("text_primary", theme.TEXT_PRIMARY)
    TYPE_COLOR = theme.color("text_secondary", theme.TEXT_SECONDARY)

    # Fonts (charter 98): label = title size, type = label size
    LABEL_FONT = QFont(theme.FONT_FAMILY, theme.NODE_TITLE_FONT_SIZE_PX)
    TYPE_FONT = QFont(theme.FONT_FAMILY, theme.NODE_LABEL_FONT_SIZE_PX)

    # Inner margin of the card content (px)
    CONTENT_MARGIN = 8.0

    # Invisible cell grid (RG065): on release, the card snaps to the nearest
    # cell of this grid; cell = card + gutter (multiples of the dot spacing,
    # so the dots stay aligned inside cells). TSK31: the grid is offset by the
    # inter-card gutter so the first card keeps the same margin to the
    # top/left edges as between two cards
    CELL_WIDTH = _get_config("agents_view_cell_width", 200.0)
    CELL_HEIGHT = _get_config("agents_view_cell_height", 140.0)
    GRID_OFFSET_X = CELL_WIDTH - WIDTH
    GRID_OFFSET_Y = CELL_HEIGHT - HEIGHT

    def __init__(self, entity: Agent, layout: AgentCardLayout):
        """
        Initialize an agent card with its business entity and visual layout.

        Args:
            entity: The business entity (Agent)
            layout: The AgentCardLayout containing visual properties
        """
        super().__init__(entity, layout)
        self.update_entity_data()

    def _init_label(self) -> None:
        """Two stacked texts: the label (lb) reuses the BaseNode label item,
        the type gets its own item at the bottom of the card."""
        self.label_item = self.label
        self.label_item.setFont(self.LABEL_FONT)
        self.label_item.setDefaultTextColor(self.TEXT_COLOR)
        self.label_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.label_item.setFlag(QGraphicsItem.ItemIsMovable, False)

        self.type_item = QGraphicsTextItem(self)
        self.type_item.setFont(self.TYPE_FONT)
        self.type_item.setDefaultTextColor(self.TYPE_COLOR)
        self.type_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.type_item.setFlag(QGraphicsItem.ItemIsMovable, False)

    def _position_label(self) -> None:
        self._position_content()

    def _init_ports(self) -> None:
        """No ports on an agent card (RG066)."""
        self.input_port = None
        self.output_port = None

    def _type_border_color(self) -> QColor:
        """Card outline color: the sand accent (TSC session 04)."""
        return self.CARD_BORDER_COLOR

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    def _position_content(self) -> None:
        """Stack the label (word-wrapped) and the type inside the card."""
        rect = self.rect()
        content_width = rect.width() - 2 * self.CONTENT_MARGIN
        self.label_item.setTextWidth(content_width)
        self.label_item.setPos(self.CONTENT_MARGIN, self.CONTENT_MARGIN)
        type_rect = self.type_item.boundingRect()
        self.type_item.setPos(
            self.CONTENT_MARGIN,
            rect.height() - self.CONTENT_MARGIN - type_rect.height()
        )

    def update_entity_data(self) -> None:
        """Refresh the card content (label, type) and the tooltip (lb + note,
        RG054) after the entity was updated."""
        lb = getattr(self.entity, 'lb', '')
        typ = getattr(self.entity, 'typ', '')
        self.label_item.setPlainText(str(lb))
        self.type_item.setPlainText(str(typ))
        self._position_content()
        note = getattr(self.entity, 'note', None)
        tooltip = str(lb) if lb else ''
        if note:
            tooltip += f"\n{note}" if tooltip else str(note)
        self.setToolTip(tooltip)

    # ------------------------------------------------------------------
    # QGraphicsItem overrides (card-specific behavior only; paint, shape,
    # boundingRect, hover, mousePress/Move, update_layout, position
    # observers and the selection outline come from BaseNode)
    # ------------------------------------------------------------------

    def mouseReleaseEvent(self, event) -> None:
        # Bypass BaseNode.mouseReleaseEvent (grid snap RG046): the card snaps
        # to the invisible cell grid instead (RG065, below)
        QGraphicsRectItem.mouseReleaseEvent(self, event)
        # RG065: on release, snap to the nearest cell of the invisible grid
        # (nearest FREE cell when the target cell is occupied)
        target = self._cell_snap_target(self.pos())
        if target != self.pos():
            self.setPos(target)
        self.update_layout()
        self._notify_position_observers()

    def _cell_snap_target(self, pos: QPointF) -> QPointF:
        """Target position on release (RG065/TSK23): nearest cell of the
        invisible grid (CELL_WIDTH x CELL_HEIGHT, anchored on the scene
        origin), clamped to the allowed region; if that cell is occupied by
        another card, the nearest free cell. The allowed region is the scene
        intersected with the bounding box of the OTHER cards expanded by one
        cell on each side (TSK23: the group can only grow by one cell per
        move); with a single card (no others) the whole scene stays allowed."""
        x = LayoutService.snap_to_grid(pos.x(), self.CELL_WIDTH, self.GRID_OFFSET_X)
        y = LayoutService.snap_to_grid(pos.y(), self.CELL_HEIGHT, self.GRID_OFFSET_Y)
        width = self.rect().width()
        height = self.rect().height()
        scene = self.scene()
        if scene is None:
            return QPointF(x, y)
        scene_rect = scene.sceneRect()
        others = [(it.pos().x(), it.pos().y(), it.rect().width(), it.rect().height())
                  for it in scene.items()
                  if isinstance(it, AgentCardItem) and it is not self]
        left, top = scene_rect.left(), scene_rect.top()
        right, bottom = scene_rect.right(), scene_rect.bottom()
        if others:
            left = max(left, min(o[0] for o in others) - self.CELL_WIDTH)
            top = max(top, min(o[1] for o in others) - self.CELL_HEIGHT)
            right = min(right, max(o[0] + o[2] for o in others) + self.CELL_WIDTH)
            bottom = min(bottom, max(o[1] + o[3] for o in others) + self.CELL_HEIGHT)
        x = max(left, min(x, right - width))
        y = max(top, min(y, bottom - height))
        free_x, free_y = LayoutService.find_nearest_free_position(
            x, y, width, height, others, self.CELL_WIDTH, self.CELL_HEIGHT,
            bounds=(left, top, right, bottom))
        return QPointF(free_x, free_y)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.ItemSelectedChange:
            # The selected card is raised above the others, so a card
            # dragged over a neighbour never disappears behind it
            self.setZValue(1.0 if value else 0.0)
        # Position clamping and selection appearance: BaseNode.itemChange
        return super().itemChange(change, value)
