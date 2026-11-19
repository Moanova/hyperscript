# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : relationships_workspace.py
# Version      : 2
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Relationships workspace (TSK27, rewritten TSK29): the widget of the
"Relationships" tab.

TSK29 - closer to the planoscript Agent x State matrix (figé faa8fdd), per the
design note docs/conception/04_relationships_matrix-FR/EN.md:
- custom graphics scene (no QTableWidget): square cells
  (`relationships_view_cell_size_px` = 100), background grid on the visible
  area only; header cards with the narrative-block rendering (MatrixAgentCard,
  80x40, sand border) - rows on the left, columns on top;
- rows and columns have INDEPENDENT orders (RG070 revised session 09):
  initial alphabetical (label, ties by id), reordering by dragging a header
  card (move constrained to the card's axis), both orders persisted at
  project level (`relationships_view_row_order` / `column_order`, RG067);
- cell (A, B) shows the type of the pair's derived state at the selected block
  (RG069 - RelationshipService.pair_state_at_block) and is a CLICKABLE object:
  left click opens the creation dialog (pair + current block pre-filled) or
  the edit dialog of the existing relationship; right click opens the context
  menu (built by MainWindow, RG055);
- right side panel: two filter zones (journey, agent - mirrors of the Display
  menu, state owned by MainWindow) then the block list, top to bottom by
  minimum rank across all journeys (ties by id - RG069), restricted to the
  blocks visible under the active filters (intersection RG064);
- default selected block: the Start block (RG068); when arriving from a block
  selected in "Journeys", that block if it belongs to the active filter,
  otherwise the Start (RG069);
- filters (RG048/RG063/RG064): cells whose relationship is outside the filter
  are dimmed and not clickable; with the agent filter active, uninvolved
  agents' header cards are dimmed and cells of a pair not involving the
  filtered agent are not clickable (creation forbidden - RG069).

The workspace NEVER writes the business model (RG058): it emits signals and
the MainWindow applies the use cases.
"""
import logging
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QFrame, QComboBox, QListWidget,
    QListWidgetItem, QLabel,
)
from PySide6.QtCore import Qt, Signal, QPointF, QEvent
from PySide6.QtGui import QColor, QBrush, QPen, QPainter, QPainterPath, QPainterPathStroker, QFont

from core.models.data_model import NarrativeMap, Project
from core.models.view_model import ProjectLayout
from core.services.journey_filter_service import JourneyFilterService
from core.services.agent_filter_service import AgentFilterService
from core.services.relationship_service import RelationshipService
from ui.nodes.matrix_agent_card import MatrixAgentCard
from config.config_loader import get as _get_config
from ui.utils import theme

_PANEL_WIDTH = int(_get_config("relationships_view_panel_width_px", 260))
_CELL_SIZE = int(_get_config("relationships_view_cell_size_px", 100))  # square cells (TSK29)
_TYPE_COLORS = _get_config("relationship_type_colors", {})
_FALLBACK_TYPE_COLOR = _get_config("block_scene_color", "#E5C07B")
_ALL_JOURNEYS_LABEL = _get_config("journey_list_all_label", "All journeys")
_ALL_AGENTS_LABEL = _get_config("agent_list_all_label", "All agents")
_BG_PRIMARY = _get_config("bg_primary", theme.BG_PRIMARY)
_GRID_MINOR_COLOR = _get_config("grid_minor_color", "#333333")
_GRID_MAJOR_COLOR = _get_config("grid_major_color", "#4A4A4A")
_BORDER_COLOR = _get_config("border_color", "#383838")
_TEXT_PRIMARY = _get_config("text_primary", theme.TEXT_PRIMARY)
_TEXT_SECONDARY = _get_config("text_secondary", theme.TEXT_SECONDARY)
_CELL_TEXT_COLOR = _get_config("badge_text_color", "#1E1E1E")
_CELL_HIT_WIDTH = _get_config("journeys_view_hit_area_width_px", 12.0)
_CELL_MARGIN = 2.0
_CARD_W = MatrixAgentCard.WIDTH
_CARD_H = MatrixAgentCard.HEIGHT
_CARD_OFF_X = (_CELL_SIZE - _CARD_W) / 2   # 10 px at C=100 -> 20 px between adjacent cards
_CARD_OFF_Y = (_CELL_SIZE - _CARD_H) / 2   # 30 px at C=100
_CELLS_LEFT = _CELL_SIZE    # cells area starts after the row-header column
_CELLS_TOP = _CELL_SIZE     # ... and after the column-header row

logger = logging.getLogger(__name__)


class _MatrixCell(QGraphicsRectItem):
    """One clickable matrix cell (row, col): type text on the type color."""

    def __init__(self, row: int, col: int):
        super().__init__(0, 0, _CELL_SIZE - 2 * _CELL_MARGIN, _CELL_SIZE - 2 * _CELL_MARGIN)
        self.row = row
        self.col = col
        self.clickable = True
        self.typ = None
        self.note = None
        self.dimmed = False
        self.setPos(_CELLS_LEFT + col * _CELL_SIZE + _CELL_MARGIN,
                    _CELLS_TOP + row * _CELL_SIZE + _CELL_MARGIN)
        self.setZValue(0)

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(_CELL_HIT_WIDTH)
        path = QPainterPath()
        path.addRect(self.rect())
        return stroker.createStroke(path).united(path)

    def set_content(self, typ: Optional[str], note: Optional[str], dimmed: bool):
        self.typ = typ
        self.note = note
        self.dimmed = dimmed
        self.setToolTip(note or "")
        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        rect = self.rect()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.typ is not None:
            color = _TYPE_COLORS.get(self.typ, _FALLBACK_TYPE_COLOR)
            painter.setBrush(QBrush(QColor(color)))
            text_color = _CELL_TEXT_COLOR
        else:
            painter.setBrush(QBrush(QColor(_BG_PRIMARY)))
            text_color = _TEXT_SECONDARY
        pen = QPen(QColor(_BORDER_COLOR), 1.0)
        painter.setPen(pen)
        painter.drawRect(rect)
        if self.dimmed:
            painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)
        if self.typ is not None:
            font = QFont(_get_config("node_font_family", "Segoe UI"), _get_config("node_label_font_size_px", 9))
            painter.setFont(font)
            painter.setPen(QPen(QColor(text_color)))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.typ)


class _MatrixGraphicsView(QGraphicsView):
    """Graphics view of the matrix; mouse handling delegates to the workspace
    (card drag constrained to its axis, cell click, context menu)."""

    def __init__(self, workspace: 'RelationshipsWorkspace'):
        super().__init__()
        self._workspace = workspace
        self.setFrameShape(QFrame.NoFrame)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._dragged_card = None

    def viewportEvent(self, event):
        # Swallow Qt's delayed automatic tooltip (AGENTS.md pattern)
        if event.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(event)

    def _scene_pos(self, event):
        return self.mapToScene(event.position().toPoint())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self._scene_pos(event)
            card = self._workspace._card_at(pos)
            if card is not None:
                if not card.isSelected():
                    self._workspace.scene.clearSelection()
                    card.setSelected(True)
                self._dragged_card = card
                event.accept()
                return
            cell = self._workspace._cell_at(pos)
            if cell is not None and cell.clickable and not cell.dimmed:
                self._workspace.scene.clearSelection()
                self._workspace.cell_clicked.emit(cell.row, cell.col)
                event.accept()
                return
            self._workspace.scene.clearSelection()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragged_card is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._workspace._on_card_dragged(self._dragged_card, self._scene_pos(event))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragged_card is not None:
            self._workspace._on_card_released(self._dragged_card, self._scene_pos(event))
            self._dragged_card = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        pos = self._scene_pos(event)
        cell = self._workspace._cell_at(pos)
        if cell is not None:
            self._workspace.context_menu_requested.emit(
                cell.row, cell.col, self.viewport().mapToGlobal(event.position().toPoint()))
            event.accept()
            return
        super().contextMenuEvent(event)


class RelationshipsWorkspace(QWidget):
    """Workspace of the "Relationships" view: agent x agent matrix + side panel."""

    anchor_block_selected = Signal(int)              # block id (side panel list)
    journey_filter_requested = Signal(bool)          # mirror of Display > Journey
    agent_filter_requested = Signal(object)          # agent id or None
    cell_clicked = Signal(int, int)                  # row, col (left click, TSK29)
    context_menu_requested = Signal(int, int, object)  # row, col, global QPoint
    axis_order_changed = Signal(list, list)          # row_order, col_order (RG070)
    workspace_modified = Signal()

    def __init__(self, project: Project, narrative_map: NarrativeMap,
                 info_bar=None, main_window=None):
        super().__init__()
        self.project = project
        self.narrative_map = narrative_map
        self.info_bar = info_bar
        self._main_window = main_window
        self._row_order: List[int] = []     # agent ids, rows (left headers)
        self._col_order: List[int] = []     # agent ids, columns (top headers)
        self._row_cards: Dict[int, MatrixAgentCard] = {}
        self._col_cards: Dict[int, MatrixAgentCard] = {}
        self._cells: Dict[Tuple[int, int], _MatrixCell] = {}
        self._block_ids: List[int] = []
        self._anchor_block_id: Optional[int] = None
        self._journey_filter_active = False
        self._agent_filter_agent_id: Optional[int] = None
        self._updating_combos = False
        self._updating_blocks = False
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Horizontal, self)
        layout.addWidget(splitter)

        self.scene = QGraphicsScene()
        self.view = _MatrixGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setBackgroundBrush(QBrush(QColor(_BG_PRIMARY)))
        splitter.addWidget(self.view)

        panel = QWidget()
        panel.setFixedWidth(_PANEL_WIDTH)
        panel.setStyleSheet(f"background-color: {_get_config('bg_surface', theme.BG_SURFACE)};")
        panel_layout = QVBoxLayout(panel)
        panel_layout.addWidget(QLabel("Journey"))
        self.journey_combo = QComboBox()
        self.journey_combo.currentIndexChanged.connect(self._on_journey_combo)
        panel_layout.addWidget(self.journey_combo)
        panel_layout.addWidget(QLabel("Agent"))
        self.agent_combo = QComboBox()
        self.agent_combo.currentIndexChanged.connect(self._on_agent_combo)
        panel_layout.addWidget(self.agent_combo)
        panel_layout.addWidget(QLabel("Blocks"))
        self.block_list = QListWidget()
        self.block_list.currentRowChanged.connect(self._on_block_selected)
        panel_layout.addWidget(self.block_list, stretch=1)
        splitter.addWidget(panel)
        splitter.setStretchFactor(0, 1)

    # ------------------------------------------------------------------
    # Populate / refresh
    # ------------------------------------------------------------------
    def populate(self, project: Project, narrative_map: NarrativeMap,
                 project_layout: Optional[ProjectLayout] = None):
        """Fill the view from the model; row/column orders from the saved
        project layout (RG070), new agents appended alphabetically (label, id)."""
        self.project = project
        self.narrative_map = narrative_map
        agents = list(project.agent)
        saved_row = project_layout.relationships_view_row_order if project_layout else []
        saved_col = project_layout.relationships_view_column_order if project_layout else []
        self._row_order = RelationshipService.resolve_axis_order(agents, saved_row)
        self._col_order = RelationshipService.resolve_axis_order(agents, saved_col)
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        start = next((b for b in narrative_map.block if b.typ == "Start"), None)  # RG025/RG068
        self._anchor_block_id = start.id if start is not None else (
            narrative_map.block[0].id if narrative_map.block else None)
        self._relayout()
        self._rebuild_cells()
        self._sync_block_list_selection()

    def refresh(self):
        """Recompute from the model (agents/blocks/relationships changed);
        keeps current orders, anchor block and filters."""
        agents = list(self.project.agent)
        known = {a.id for a in agents}
        self._row_order = [i for i in self._row_order if i in known] + \
            [a.id for a in sorted(agents, key=lambda a: (a.lb, a.id)) if a.id not in self._row_order]
        self._col_order = [i for i in self._col_order if i in known] + \
            [a.id for a in sorted(agents, key=lambda a: (a.lb, a.id)) if a.id not in self._col_order]
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        if self._anchor_block_id is None or self._anchor_block_id not in self._block_ids:
            start = next((b for b in self.narrative_map.block if b.typ == "Start"), None)
            self._anchor_block_id = start.id if start is not None else (
                self._block_ids[0] if self._block_ids else None)
        self._relayout()
        self._rebuild_cells()
        self._sync_block_list_selection()

    def collect_project_layout(self, layout: ProjectLayout):
        """RG070 (revised session 09): persist both independent orders at project level."""
        layout.relationships_view_row_order = list(self._row_order)
        layout.relationships_view_column_order = list(self._col_order)

    def get_anchor_block_id(self) -> Optional[int]:
        return self._anchor_block_id

    def agent_id_at_row(self, row: int) -> Optional[int]:
        return self._row_order[row] if 0 <= row < len(self._row_order) else None

    def agent_id_at_col(self, col: int) -> Optional[int]:
        return self._col_order[col] if 0 <= col < len(self._col_order) else None

    # ------------------------------------------------------------------
    # Scene geometry / layout
    # ------------------------------------------------------------------
    def _card_at(self, pos: QPointF):
        for card in list(self._row_cards.values()) + list(self._col_cards.values()):
            if card.shape().contains(pos):
                return card
        return None

    def _cell_at(self, pos: QPointF):
        for cell in self._cells.values():
            if cell.shape().contains(pos):
                return cell
        return None

    def _relayout(self):
        """(Re)create and position header cards and cells from the orders."""
        agents = {a.id: a for a in self.project.agent}
        # row header cards (left column)
        for i, aid in enumerate(self._row_order):
            card = self._row_cards.get(aid)
            if card is None:
                card = MatrixAgentCard(agents[aid], 'row')
                self.scene.addItem(card)
                self._row_cards[aid] = card
            card.setPos(_CARD_OFF_X, _CELLS_TOP + i * _CELL_SIZE + _CARD_OFF_Y)
        # column header cards (top row)
        for j, aid in enumerate(self._col_order):
            card = self._col_cards.get(aid)
            if card is None:
                card = MatrixAgentCard(agents[aid], 'column')
                self.scene.addItem(card)
                self._col_cards[aid] = card
            card.setPos(_CELLS_LEFT + j * _CELL_SIZE + _CARD_OFF_X, _CARD_OFF_Y)
        # cells
        for i in range(len(self._row_order)):
            for j in range(len(self._col_order)):
                cell = self._cells.get((i, j))
                if cell is None:
                    cell = _MatrixCell(i, j)
                    self.scene.addItem(cell)
                    self._cells[(i, j)] = cell
        # scene rect
        w = _CELLS_LEFT + len(self._col_order) * _CELL_SIZE + _CELL_SIZE
        h = _CELLS_TOP + len(self._row_order) * _CELL_SIZE + _CELL_SIZE
        self.scene.setSceneRect(0, 0, max(w, 400), max(h, 300))
        self._draw_grid()

    def _draw_grid(self):
        """Background grid on the visible area only; non-interactive lines."""
        for item in list(self.scene.items()):
            if getattr(item, '_is_grid_line', False):
                self.scene.removeItem(item)
        rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        n_cols = len(self._col_order) + 1
        n_rows = len(self._row_order) + 1
        for j in range(n_cols + 1):
            x = j * _CELL_SIZE
            if rect.left() - _CELL_SIZE <= x <= rect.right() + _CELL_SIZE:
                line = self.scene.addLine(x, 0, x, _CELLS_TOP + n_rows * _CELL_SIZE)
                line.setPen(QPen(QColor(_GRID_MAJOR_COLOR if j % 4 == 0 else _GRID_MINOR_COLOR), 1))
                line.setZValue(-2)
                line._is_grid_line = True
        for i in range(n_rows + 1):
            y = i * _CELL_SIZE
            if rect.top() - _CELL_SIZE <= y <= rect.bottom() + _CELL_SIZE:
                line = self.scene.addLine(0, y, _CELLS_LEFT + n_cols * _CELL_SIZE, y)
                line.setPen(QPen(QColor(_GRID_MAJOR_COLOR if i % 4 == 0 else _GRID_MINOR_COLOR), 1))
                line.setZValue(-2)
                line._is_grid_line = True

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._draw_grid()

    # ------------------------------------------------------------------
    # Cells content (derived state at the anchor block, RG069) + filters
    # ------------------------------------------------------------------
    def _visible_relationship_ids(self):
        nm = self.narrative_map
        vis = set(JourneyFilterService.visible_relationship_ids(nm))
        if self._journey_filter_active:
            active = nm.get_active_journey()
            vis &= JourneyFilterService.visible_relationship_ids(nm, active.id if active else None)
        if self._agent_filter_agent_id is not None:
            vis &= AgentFilterService.visible_relationship_ids(nm, self._agent_filter_agent_id)
        return vis

    def _rebuild_cells(self):
        nm = self.narrative_map
        vis_rel = self._visible_relationship_ids()
        filtered_agent = self._agent_filter_agent_id
        for (i, j), cell in self._cells.items():
            if i == j:
                cell.set_content(None, None, dimmed=True)
                cell.clickable = False
                cell.setEnabled(False)
                continue
            ai = self.agent_id_at_row(i)
            aj = self.agent_id_at_col(j)
            rel = None
            if ai is not None and aj is not None and self._anchor_block_id is not None:
                rel = RelationshipService.pair_state_at_block(nm, ai, aj, self._anchor_block_id)
            dimmed = False
            clickable = True
            if rel is not None and rel.id not in vis_rel:
                dimmed = True
                clickable = False  # RG048/RG063: outside the filter, non-interactive
            if filtered_agent is not None and ai is not None and aj is not None \
                    and filtered_agent not in (ai, aj):
                clickable = False  # RG069: creation forbidden for uninvolved agents
            cell.set_content(rel.typ if rel else None, rel.note if rel else None, dimmed)
            cell.clickable = clickable
            cell.setEnabled(clickable)
        self._dim_filtered_agents()

    def _dim_filtered_agents(self):
        """RG069: with the agent filter active, uninvolved agents' header cards are dimmed."""
        for cards in (self._row_cards, self._col_cards):
            for aid, card in cards.items():
                dimmed = self._agent_filter_agent_id is not None and aid != self._agent_filter_agent_id
                card.setOpacity(JourneyFilterService.filter_opacity() if dimmed else 1.0)

    # ------------------------------------------------------------------
    # Header card drag (reorder, constrained to the card's axis - RG070)
    # ------------------------------------------------------------------
    def _on_card_dragged(self, card: MatrixAgentCard, scene_pos: QPointF):
        if card.kind == 'column':
            card.setPos(scene_pos.x() - _CARD_W / 2, _CARD_OFF_Y)
        else:
            card.setPos(_CARD_OFF_X, scene_pos.y() - _CARD_H / 2)

    def _on_card_released(self, card: MatrixAgentCard, scene_pos: QPointF):
        if card.kind == 'column':
            target = round((scene_pos.x() - _CELLS_LEFT - _CARD_OFF_X) / _CELL_SIZE)
            self._reorder(self._col_order, target, card.entity.id)
        else:
            target = round((scene_pos.y() - _CELLS_TOP - _CARD_OFF_Y) / _CELL_SIZE)
            self._reorder(self._row_order, target, card.entity.id)
        self._relayout()
        self._rebuild_cells()
        self.axis_order_changed.emit(list(self._row_order), list(self._col_order))
        self.workspace_modified.emit()

    def _reorder(self, order: List[int], target: int, agent_id: int):
        target = max(0, min(target, len(order) - 1))
        current = order.index(agent_id)
        if target == current:
            return
        order.pop(current)
        order.insert(target, agent_id)

    # ------------------------------------------------------------------
    # Filters (pushed by MainWindow; the panel zones only request changes)
    # ------------------------------------------------------------------
    def set_journey_filter_active(self, active: bool):
        self._journey_filter_active = active
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        self._rebuild_cells()

    def set_agent_filter(self, agent_id: Optional[int]):
        self._agent_filter_agent_id = agent_id
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        self._rebuild_cells()

    def _rebuild_filter_combos(self):
        self._updating_combos = True
        try:
            nm = self.narrative_map
            self.journey_combo.clear()
            self.journey_combo.addItem(_ALL_JOURNEYS_LABEL, None)
            for j in nm.journey:
                self.journey_combo.addItem(j.lb, j.id)
            if self._journey_filter_active:
                active = nm.get_active_journey()
                idx = self.journey_combo.findData(active.id if active else None)
                self.journey_combo.setCurrentIndex(idx if idx >= 0 else 0)
            else:
                self.journey_combo.setCurrentIndex(0)
            self.agent_combo.clear()
            self.agent_combo.addItem(_ALL_AGENTS_LABEL, None)
            for a in sorted(self.project.agent, key=lambda a: (a.lb, a.id)):
                self.agent_combo.addItem(f"{a.lb} ({a.typ})", a.id)
            idx = self.agent_combo.findData(self._agent_filter_agent_id)
            self.agent_combo.setCurrentIndex(idx if idx >= 0 else 0)
        finally:
            self._updating_combos = False

    def _on_journey_combo(self, index):
        if self._updating_combos:
            return
        self.journey_filter_requested.emit(self.journey_combo.itemData(index) is not None)

    def _on_agent_combo(self, index):
        if self._updating_combos:
            return
        self.agent_filter_requested.emit(self.agent_combo.itemData(index))

    # ------------------------------------------------------------------
    # Side panel block list (RG069: min rank across all journeys, ties by id,
    # restricted to blocks visible under the active filters - RG064)
    # ------------------------------------------------------------------
    def _rebuild_block_list(self):
        self._updating_blocks = True
        try:
            nm = self.narrative_map
            visible = set(RelationshipService.ordered_anchor_block_ids(nm))
            if self._journey_filter_active:
                active = nm.get_active_journey()
                visible &= JourneyFilterService.visible_block_ids(nm, active.id if active else None)
            if self._agent_filter_agent_id is not None:
                visible &= AgentFilterService.visible_block_ids(nm, self._agent_filter_agent_id)
            blocks = {b.id: b for b in nm.block}
            self._block_ids = [bid for bid in RelationshipService.ordered_anchor_block_ids(nm)
                               if bid in visible]
            self.block_list.clear()
            for bid in self._block_ids:
                b = blocks[bid]
                item = QListWidgetItem(f"{b.lb} ({b.typ})")
                item.setData(Qt.UserRole, bid)
                self.block_list.addItem(item)
        finally:
            self._updating_blocks = False
        self._sync_block_list_selection()

    def _sync_block_list_selection(self):
        if self._anchor_block_id in self._block_ids:
            row = self._block_ids.index(self._anchor_block_id)
            self.block_list.blockSignals(True)
            self.block_list.setCurrentRow(row)
            self.block_list.blockSignals(False)

    def _on_block_selected(self, row):
        if self._updating_blocks or not (0 <= row < len(self._block_ids)):
            return
        bid = self._block_ids[row]
        self._anchor_block_id = bid
        self._rebuild_cells()
        self.anchor_block_selected.emit(bid)

    def set_anchor_block(self, block_id: int):
        """Select the given block in the panel and recompute the matrix (RG069)."""
        if block_id in self._block_ids:
            self._anchor_block_id = block_id
            self._sync_block_list_selection()
            self._rebuild_cells()
