# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agent_card.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Agent card of the "Agents" view (TSK19b, RG065/RG066).

Visual representation of a project Agent (RG057), re-designed session 04:
a card larger than a narrative block (agents_view_card_width x
agents_view_card_height, config.json), WITHOUT ports and WITHOUT a
participation-count badge (participations/relationships are handled in
other views). The card shows the agent label and type; the note is shown
in an immediate hover tooltip (RG054).

The card is freely movable WITHOUT magnetic snapping (RG065, TSC session 04:
snapping on the dots or on a major grid made the moves awkward). During a
drag, the movement is constrained to a single axis — a horizontal or
vertical corridor: the dominant axis is locked when the drag starts and the
other coordinate stays at its drag-start value. The visible dots stay purely
decorative. Single selection (RG049), dashed selection outline in the card
color (charter 98: selection > hover > type), hit-testing via shape()
(RG053).

The card accent color is the sand accent (block_scene_color, #E5C07B) —
TSC feedback session 04: the card outline is sand, not gold (the gold
#D19A66 was the initial choice, planoscript reference: agent cards used
the event tint copper).
"""

from typing import Any, Optional

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QToolTip
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath

from core.models.data_model import Agent
from core.models.view_model import AgentCardLayout
from config.config_loader import get as _get_config
from ui.utils import theme


class AgentCardItem(QGraphicsRectItem):
    """Visual representation of an Agent entity in the "Agents" workspace."""

    # Card dimensions (config.json, larger than a block 80x40)
    WIDTH = _get_config("agents_view_card_width", 160.0)
    HEIGHT = _get_config("agents_view_card_height", 100.0)

    # Corner radius of the card rectangle (same as blocks, charter 98)
    CORNER_RADIUS = _get_config("node_corner_radius_px", 6.0)

    # Dash pattern of the selection outline (config.json, TSK16)
    SELECTION_DASH_PATTERN = _get_config("node_selection_dash_pattern", [4.0, 4.0])

    # Corridor (lane) drag: once the drag delta exceeds this threshold on an
    # axis, that axis is locked for the whole drag and the card slides in a
    # horizontal or vertical corridor (RG065 — no magnetic snap)
    AXIS_LOCK_THRESHOLD_PX = 4.0

    # Colors (dark theme via ui.utils.theme; no hard-coded values)
    DEFAULT_BG_COLOR = theme.color("bg_surface", theme.BG_SURFACE)
    CARD_BORDER_COLOR = theme.color("block_scene_color", theme.BLOCK_SCENE_COLOR)  # sand (TSC session 04)
    HOVER_BORDER_COLOR = theme.color("hover_color", theme.HOVER_COLOR)
    TEXT_COLOR = theme.color("text_primary", theme.TEXT_PRIMARY)
    TYPE_COLOR = theme.color("text_secondary", theme.TEXT_SECONDARY)

    # Fonts (charter 98): label = title size, type = label size
    LABEL_FONT = QFont(theme.FONT_FAMILY, theme.NODE_TITLE_FONT_SIZE_PX)
    TYPE_FONT = QFont(theme.FONT_FAMILY, theme.NODE_LABEL_FONT_SIZE_PX)

    # Inner margin of the card content (px)
    CONTENT_MARGIN = 8.0

    def __init__(self, entity: Agent, layout: AgentCardLayout):
        """
        Initialize an agent card with its business entity and visual layout.

        Args:
            entity: The business entity (Agent)
            layout: The AgentCardLayout containing visual properties
        """
        width = layout.width if layout.width > 0 else self.WIDTH
        height = layout.height if layout.height > 0 else self.HEIGHT
        super().__init__(0, 0, width, height)

        self.entity = entity
        self.layout = layout

        self.setPos(layout.x, layout.y)

        # Drag bookkeeping: Qt recomputes each ItemPositionChange proposal
        # from the last RETURNED position, so the unsnapped position is
        # accumulated here to keep the drag smooth. _drag_start/_lock_axis
        # implement the corridor (lane) drag: the dominant axis is locked at
        # drag start, the other coordinate stays at its drag-start value
        self._free_pos = QPointF(layout.x, layout.y)
        self._applied_pos = QPointF(layout.x, layout.y)
        self._drag_start = None
        self._lock_axis = None

        # Movable + selectable; no ports on an agent card (RG066)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setAcceptHoverEvents(True)

        self._hovered = False

        self.setPen(QPen(self.CARD_BORDER_COLOR, 2))
        self.setBrush(QBrush(self.DEFAULT_BG_COLOR))

        # Label (lb) and type, stacked from the top of the card
        self.label_item = QGraphicsTextItem(self)
        self.label_item.setFont(self.LABEL_FONT)
        self.label_item.setDefaultTextColor(self.TEXT_COLOR)
        self.label_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.label_item.setFlag(QGraphicsItem.ItemIsMovable, False)

        self.type_item = QGraphicsTextItem(self)
        self.type_item.setFont(self.TYPE_FONT)
        self.type_item.setDefaultTextColor(self.TYPE_COLOR)
        self.type_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.type_item.setFlag(QGraphicsItem.ItemIsMovable, False)

        self._position_content()
        self.update_entity_data()

        self._position_observers = []

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

    def update_layout(self) -> None:
        """Update the layout object with the card's current properties."""
        self.layout.x = self.x()
        self.layout.y = self.y()
        self.layout.width = self.rect().width()
        self.layout.height = self.rect().height()
        self.layout.selected = self.isSelected()

    # ------------------------------------------------------------------
    # Appearance (charter 98: selection > hover > card color)
    # ------------------------------------------------------------------

    def _apply_outline(self, selected: Optional[bool] = None) -> None:
        """Apply the outline: dashed card color when selected, soft white on
        hover, plain card color otherwise. A custom dash pattern is only
        honored by Qt for DashLine pens."""
        if selected if selected is not None else self.isSelected():
            pen = QPen(self.CARD_BORDER_COLOR, 2)
            pen.setStyle(Qt.DashLine)
            pen.setDashPattern(self.SELECTION_DASH_PATTERN)
            pen.setCapStyle(Qt.FlatCap)
            self.setPen(pen)
        elif self._hovered:
            self.setPen(QPen(self.HOVER_BORDER_COLOR, 2))
        else:
            self.setPen(QPen(self.CARD_BORDER_COLOR, 2))

    def set_selected_appearance(self, selected: bool) -> None:
        """Update the card's outline based on the selection state."""
        self._apply_outline(selected)

    # ------------------------------------------------------------------
    # QGraphicsItem overrides
    # ------------------------------------------------------------------

    def _rounded_path(self) -> QPainterPath:
        """Return the card rectangle as a rounded-corner path (charter 98)."""
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.CORNER_RADIUS, self.CORNER_RADIUS)
        return path

    def boundingRect(self):
        """Bounding rect covering the rounded outline (pen width included)."""
        return self._rounded_path().boundingRect().adjusted(-2, -2, 2, 2)

    def shape(self):
        """Clickable shape: the rounded rectangle (hit-testing, RG053)."""
        return self._rounded_path()

    def paint(self, painter, option, widget=None) -> None:
        """Paint the card as a rounded rectangle (charter 98: radius ~6px,
        no drop shadow)."""
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPath(self._rounded_path())

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        self.set_selected_appearance(self.isSelected())
        # A new drag starts: remember the start position and reset the
        # corridor axis lock
        self._drag_start = QPointF(self.pos())
        self._lock_axis = None

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        self._lock_axis = None
        if self.isSelected():
            self.update_layout()

    def mouseMoveEvent(self, event) -> None:
        super().mouseMoveEvent(event)
        if event.buttons() == Qt.LeftButton:
            self.update_layout()

    def hoverEnterEvent(self, event) -> None:
        """Hover: soft white outline; tooltip (lb + note) shown IMMEDIATELY,
        bypassing the system hover delay. The workspace swallows Qt's delayed
        automatic tooltip event (see AgentsWorkspace.viewportEvent)."""
        self._hovered = True
        self._apply_outline()
        tooltip = self.toolTip()
        if tooltip:
            QToolTip.showText(event.screenPos(), tooltip)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self._hovered = False
        self._apply_outline()
        QToolTip.hideText()
        super().hoverLeaveEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.ItemSelectedChange:
            self.set_selected_appearance(bool(value))
            self.layout.selected = bool(value)
            # The selected card is raised above the others, so a card
            # dragged over a neighbour never disappears behind it
            self.setZValue(1.0 if value else 0.0)
        elif change == QGraphicsItem.ItemPositionChange:
            # RG065 corridor drag: constrain to the scene limits, then, for a
            # mouse drag, project onto the locked axis (horizontal or
            # vertical corridor). NO magnetic snap: the position stays free.
            # The unsnapped position is accumulated from the delta against
            # the last applied position, because Qt bases each new proposal
            # on that returned value — without this accumulation, small
            # deltas would be swallowed and the card would not move.
            new_pos = value
            scene = self.scene()
            if scene:
                scene_rect = scene.sceneRect()
                card_width = self.rect().width()
                card_height = self.rect().height()

                delta = new_pos - self._applied_pos
                self._free_pos += delta

                free_x = max(scene_rect.left(), min(self._free_pos.x(), scene_rect.right() - card_width))
                free_y = max(scene_rect.top(), min(self._free_pos.y(), scene_rect.bottom() - card_height))
                self._free_pos = QPointF(free_x, free_y)

                # Corridor lock: once the drag exceeds the threshold on an
                # axis, that axis dominates for the whole drag; the other
                # coordinate stays at its drag-start value. Programmatic
                # setPos (no drag in progress) is never locked.
                if self._drag_start is not None:
                    dx = self._free_pos.x() - self._drag_start.x()
                    dy = self._free_pos.y() - self._drag_start.y()
                    if self._lock_axis is None and (
                            abs(dx) >= self.AXIS_LOCK_THRESHOLD_PX
                            or abs(dy) >= self.AXIS_LOCK_THRESHOLD_PX):
                        self._lock_axis = 'x' if abs(dx) >= abs(dy) else 'y'
                    if self._lock_axis == 'x':
                        free_y = self._drag_start.y()
                    elif self._lock_axis == 'y':
                        free_x = self._drag_start.x()
                    self._free_pos = QPointF(free_x, free_y)

                self._applied_pos = QPointF(free_x, free_y)
                self.layout.x = free_x
                self.layout.y = free_y

                self._notify_position_observers()
                return self._applied_pos

        return super().itemChange(change, value)

    # ------------------------------------------------------------------
    # Position observers (the workspace listens to moves, e.g. to mark the
    # project modified - FN017/RG060)
    # ------------------------------------------------------------------

    def register_position_observer(self, callback) -> None:
        if callback not in self._position_observers:
            self._position_observers.append(callback)

    def unregister_position_observer(self, callback) -> None:
        if callback in self._position_observers:
            self._position_observers.remove(callback)

    def _notify_position_observers(self) -> None:
        for callback in self._position_observers:
            callback()
