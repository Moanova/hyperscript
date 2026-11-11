# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : block_node.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Block node of the Journeys workspace (TSK10).

Visual representation of a narrative Block (any type: Start, Scene, Pivot,
Condition, End) - fusion of the planoscript StateNode/EventNode. The border
color is the block type color (config.json block_*_color, adopted session 03);
the node displays the block TYPE, and the label + note are shown in the hover
tooltip (session 03 decision, RG054).

The participation badge is kept as-is from planoscript (session 03): bottom-
right corner of the node outline, two thirds of the badge inside / one third
outside; diameter from config.json; fixed badge_bg_color fill (whatever the
block type color); hidden at 0 participation; '9+' beyond 9; non-clickable
(a click selects the node); an 'Agents:' line is added to the tooltip.
"""

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtGui import QBrush, QPen, QFont

from config.config_loader import get as _get_config
from core.models.data_model import Block
from core.models.view_model import NodeLayout
from core.services.participation_badge_service import ParticipationBadgeService
from ui.nodes.base_node import TypedNode
from ui.utils import theme


class BlockNode(TypedNode):
    """Visual representation of a Block entity in the Journeys workspace."""

    # Badge settings (config.json, Journeys view; planoscript used the events view keys)
    BADGE_DIAMETER = _get_config("journeys_view_badge_diameter_px", 16.0)
    BADGE_BG_COLOR = theme.color("badge_bg_color", theme.BADGE_BG_COLOR)
    BADGE_BORDER_COLOR = theme.color("badge_border_color", theme.BADGE_BORDER_COLOR)
    BADGE_TEXT_COLOR = theme.color("badge_text_color", theme.BADGE_TEXT_COLOR)

    def __init__(self, block: Block, layout: NodeLayout):
        super().__init__(block, layout)
        self._update_colors()
        self._init_participation_badge()

    def _init_participation_badge(self) -> None:
        """Create the participation badge items, hidden by default."""
        diameter = self.BADGE_DIAMETER
        self.participation_badge = QGraphicsEllipseItem(0, 0, diameter, diameter, self)
        self.participation_badge.setBrush(QBrush(self.BADGE_BG_COLOR))
        self.participation_badge.setPen(QPen(self.BADGE_BORDER_COLOR))
        self.participation_badge.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.participation_badge.setFlag(QGraphicsItem.ItemIsMovable, False)

        self.participation_badge_text = QGraphicsTextItem(self.participation_badge)
        font = QFont("Arial", 7)
        font.setBold(True)
        self.participation_badge_text.setFont(font)
        self.participation_badge_text.setDefaultTextColor(self.BADGE_TEXT_COLOR)

        self.participation_badge.hide()
        self._position_participation_badge()

    def _position_participation_badge(self) -> None:
        """Place the badge in the bottom-right corner of the node, mostly
        inside the outline: two thirds of the badge inside, one third outside
        (kept from planoscript, session 03).

        Guard: during BaseNode.__init__, update_from_layout() runs before
        _init_participation_badge() creates the badge items.
        """
        if getattr(self, 'participation_badge', None) is None:
            return
        diameter = self.BADGE_DIAMETER
        outside = round(diameter / 3)
        rect = self.rect()
        x = rect.width() - diameter + outside
        y = rect.height() - diameter + outside
        self.participation_badge.setPos(x, y)
        # Center the text in the badge
        text_rect = self.participation_badge_text.boundingRect()
        self.participation_badge_text.setPos(
            (diameter - text_rect.width()) / 2,
            (diameter - text_rect.height()) / 2
        )

    def refresh_participation_badge(self, count: int, agent_labels=None) -> None:
        """Refresh the participation badge from the number of participations
        of the block.

        Hidden when no agent participates; '9+' beyond 9
        (ParticipationBadgeService). The tooltip agents line is updated from
        the agent labels when provided.
        """
        self._participating_agent_labels = list(agent_labels or [])
        if ParticipationBadgeService.badge_visible(count):
            self.participation_badge_text.setPlainText(
                ParticipationBadgeService.badge_text(count))
            self._position_participation_badge()
            self.participation_badge.show()
        else:
            self.participation_badge.hide()
        # Refresh the tooltip so the agents line stays in sync
        self.update_entity_data()

    def get_participating_agent_labels(self):
        """Return the labels of the agents participating in the block."""
        return list(getattr(self, '_participating_agent_labels', []))

    def update_entity_data(self) -> None:
        """Refresh label (type) and tooltip (lb + note + agents line)."""
        super().update_entity_data()
        agents_line = ParticipationBadgeService.tooltip_agents_line(
            self.get_participating_agent_labels())
        if agents_line:
            tooltip = self.toolTip()
            self.setToolTip(tooltip + "\n" + agents_line if tooltip else agents_line)

    def update_from_layout(self) -> None:
        """Update visual properties, repositioning the badge after resize."""
        super().update_from_layout()
        self._position_participation_badge()
