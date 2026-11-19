# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : matrix_agent_card.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Header card of the "Relationships" matrix (TSK29).

MatrixAgentCard is a QGraphicsRectItem with the narrative-block rendering
(80x40, rounded corners, sand border `block_scene_color`, truncated label +
immediate tooltip RG054, enlarged shape() hit-testing RG053) but WITHOUT
ports - a distinct technical object from BlockNode. kind is 'row' (left
column header) or 'column' (top row header); the drag that reorders the
matrix is handled by the workspace view, constrained to the card's axis
(RG070 revised session 09). Selection: single, dashed outline
(node_selection_dash_pattern), via itemChange like BaseNode.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainterPathStroker, QPen, QBrush, QColor, QFont, QPainter, QToolTip

from core.models.data_model import Agent
from config.config_loader import get as _get_config
from ui.utils import theme


class MatrixAgentCard(QGraphicsRectItem):
    """Agent header card of the "Relationships" matrix (row or column)."""

    WIDTH = _get_config("node_default_width", 80.0)
    HEIGHT = _get_config("node_default_height", 40.0)
    CORNER_RADIUS = _get_config("node_corner_radius_px", 6.0)
    SELECTION_DASH_PATTERN = _get_config("node_selection_dash_pattern", [4.0, 4.0])
    HIT_AREA_WIDTH = _get_config("journeys_view_hit_area_width_px", 12.0)
    BORDER_COLOR = _get_config("block_scene_color", theme.BLOCK_SCENE_COLOR)
    BG_COLOR = _get_config("bg_surface", theme.BG_SURFACE)
    TEXT_COLOR = _get_config("text_primary", theme.TEXT_PRIMARY)
    FONT_SIZE = _get_config("node_label_font_size_px", 9)

    def __init__(self, agent: Agent, kind: str):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.entity = agent
        self.kind = kind  # 'row' (left column) or 'column' (top row)
        self._selected = False
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        tooltip = f"{agent.lb} ({agent.typ})"
        if agent.note:
            tooltip += f"\n{agent.note}"
        self.setToolTip(tooltip)
        self.itemChanged.connect(self._on_item_changed)

    def _on_item_changed(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            self._selected = bool(value)
            self.update()
        return super().itemChange(change, value)

    def shape(self):
        """RG053: clickable area = geometric shape enlarged beyond the pen."""
        path = QPainterPathStroker()
        path.setWidth(self.HIT_AREA_WIDTH)
        p = self._rect_path()
        return path.createStroke(p).united(p)

    def _rect_path(self):
        from PySide6.QtGui import QPainterPath
        p = QPainterPath()
        p.addRoundedRect(QRectF(0, 0, self.WIDTH, self.HEIGHT), self.CORNER_RADIUS, self.CORNER_RADIUS)
        return p

    def boundingRect(self):
        return QRectF(0, 0, self.WIDTH, self.HEIGHT).adjusted(
            -self.HIT_AREA_WIDTH / 2, -self.HIT_AREA_WIDTH / 2,
            self.HIT_AREA_WIDTH / 2, self.HIT_AREA_WIDTH / 2)

    def hoverEnterEvent(self, event):
        # RG054: immediate tooltip (the workspace swallows Qt's delayed one)
        QToolTip.showText(event.screenPos(), self.toolTip(), self)
        super().hoverEnterEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        rect = QRectF(0, 0, self.WIDTH, self.HEIGHT)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self.BG_COLOR)))
        pen = QPen(QColor(self.BORDER_COLOR), 2.0)
        if self._selected:
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern(self.SELECTION_DASH_PATTERN)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)
        # truncated centered label
        font = QFont(_get_config("node_font_family", "Segoe UI"), self.FONT_SIZE)
        painter.setFont(font)
        painter.setPen(QPen(QColor(self.TEXT_COLOR)))
        metrics = painter.fontMetrics()
        text = self.entity.lb
        max_width = self.WIDTH - 8
        if metrics.horizontalAdvance(text) > max_width:
            text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, int(max_width))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
