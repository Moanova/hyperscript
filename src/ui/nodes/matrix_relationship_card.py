# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : matrix_relationship_card.py
# Version      : 1
# Date         : 2026-11-20
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Relationship card inside a matrix cell of the "Relationships" view (TSK32).

MatrixRelationshipCard is a QGraphicsRectItem materializing the Relationship
entity in its (unique, upper-triangle) cell: sand-free rendering - background
`bg_surface`, 2 px border in `relationships_view_card_border_color` (the
Pivot/Condition block color #E06666, per the adopted design), rounded corners,
centered truncated label = the relationship type. The full details (type,
agent pair, anchor block, note) show in the immediate tooltip on hover
(RG054). Hit-testing through an enlarged shape() (RG053).

The card is NOT selectable and has no left-click behavior (TSK32 adopted
design: no left click in the cells - creation/edition/deletion go through the
right-click context menu, RG055). Its position is always derived from the
cell; it is never persisted.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget, QToolTip
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPen, QBrush, QColor, QFont, QPainter

from config.config_loader import get as _get_config
from ui.utils import theme


class MatrixRelationshipCard(QGraphicsRectItem):
    """Relationship card of one matrix cell (upper triangle, TSK32)."""

    # TSK36 (option 1, session 11): same size as the matrix Agent cards
    WIDTH = _get_config("node_default_width", 80.0)
    HEIGHT = _get_config("node_default_height", 40.0)
    CORNER_RADIUS = _get_config("node_corner_radius_px", 6.0)
    HIT_AREA_WIDTH = _get_config("journeys_view_hit_area_width_px", 12.0)
    BORDER_COLOR = _get_config("relationships_view_card_border_color", "#E06666")
    BG_COLOR = _get_config("bg_surface", theme.BG_SURFACE)
    TEXT_COLOR = _get_config("text_primary", theme.TEXT_PRIMARY)
    FONT_SIZE = _get_config("node_label_font_size_px", 9)

    def __init__(self, label: str = ""):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.rel_id: int | None = None
        self._label = label
        # TSK32: no left-click semantics on the cells -> not selectable
        self.setAcceptHoverEvents(True)

    def set_relationship(self, rel_id: int, label: str, tooltip: str):
        self.rel_id = rel_id
        self._label = label
        self.setToolTip(tooltip)
        self.update()

    def shape(self):
        """RG053: clickable area = geometric shape enlarged beyond the pen."""
        stroker = QPainterPathStroker()
        stroker.setWidth(self.HIT_AREA_WIDTH)
        p = QPainterPath()
        p.addRoundedRect(QRectF(0, 0, self.WIDTH, self.HEIGHT), self.CORNER_RADIUS, self.CORNER_RADIUS)
        return stroker.createStroke(p).united(p)

    def boundingRect(self):
        return QRectF(0, 0, self.WIDTH, self.HEIGHT).adjusted(
            -self.HIT_AREA_WIDTH / 2, -self.HIT_AREA_WIDTH / 2,
            self.HIT_AREA_WIDTH / 2, self.HIT_AREA_WIDTH / 2)

    def hoverEnterEvent(self, event):
        # RG054: immediate tooltip; no widget argument (QGraphicsItem is not a QWidget)
        QToolTip.showText(event.screenPos(), self.toolTip())
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        QToolTip.hideText()
        super().hoverLeaveEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        rect = QRectF(0, 0, self.WIDTH, self.HEIGHT)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self.BG_COLOR)))
        painter.setPen(QPen(QColor(self.BORDER_COLOR), 2.0))
        painter.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)
        # truncated centered label = the relationship type
        font = QFont(_get_config("node_font_family", "Segoe UI"), self.FONT_SIZE)
        painter.setFont(font)
        painter.setPen(QPen(QColor(self.TEXT_COLOR)))
        metrics = painter.fontMetrics()
        text = self._label
        max_width = self.WIDTH - 8
        if metrics.horizontalAdvance(text) > max_width:
            text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, int(max_width))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
