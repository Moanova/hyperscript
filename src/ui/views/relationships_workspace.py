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
- rows and columns had independent orders (RG070 revised session 09) until
  TSK32 (session 10): now a SINGLE shared order, upper-triangle matrix - see
  the TSK32 paragraph below;
- cell (A, B) shows the pair's derived state at the selected block (RG069 -
  RelationshipService.pair_state_at_block); until TSK32 it was a clickable
  checkbox object (left click = create/edit, right click = context menu);
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

TSK30 (session 10 test feedback): the matrix is anchored to the top-left
corner (view alignment AlignLeft|AlignTop, scene (0, 0, min 4000x4000)
growing rightwards/downwards only, scrollbars always on); the background
grid covers the whole visible area (non-interactive _GridLineItem lines,
redrawn on scroll and resize); each cell carries a center dot (agents-view
style) and a checkbox (outline only; filled gold circle when the pair has a
relationship - the type is shown in the cell tooltip); hit-testing maps
scene positions to item-local coordinates (mapFromScene); left click on an
empty cell creates an "Undefined" relationship directly (MainWindow), right
click keeps the context menu; the side panel gets a separator after the
agent filter; the journey combo emits the chosen journey id (None = All
journeys) so the MainWindow can activate it (mirror of Display > Journey).

TSK31 (session 10, 2nd feedback batch): contextMenuEvent uses QContextMenuEvent
pos()/globalPos() (no position() attribute); the diagonal is dimmed by agent
IDENTITY (ai == aj), not by index, so it follows the dragged header card with
independent row/column orders; cells are transparent (no fill/border) so the
matrix lines are the background grid lines themselves; no dots in the
background (TSK36 session 11, option 2: per-cell center dot of TSK31 2.4 and
agents-view dot field both removed); the view gets theme.WORKSPACE_STYLESHEET
so its scrollbars look/behave like the "Journeys" view; the side panel
separator is a thicker filled bar; the splitter slot of the panel is pinned
to the panel width on resize (no gray strip on the right), the panel content
is dark-themed, and the block list has an always-visible dark scrollbar
(scrollbar only in the list zone, never next to the filters).

TSK33 (session 10): the side panel is extracted into the shared widget
FiltersSidePanel (ui/widgets/filters_side_panel.py, show_block_list=True here)
hosted in a SidePanelSplitter; the filter/anchor state lives in the panel and
the workspace exposes the historical attribute names (journey_combo,
block_list, _block_ids, _anchor_block_id, ...) as delegates, so the matrix
logic and the tests are unchanged. The "Journeys" view hosts the same panel
with show_block_list=False (no block list) - see main_window.py.

TSK32 (session 10, adopted design): the symmetric matrix showed 2 checkmarks
per relationship -> the matrix becomes an UPPER-TRIANGLE matrix. Rows and
columns carry the SAME agents with a SINGLE shared order (persisted as
`relationships_view_agent_order`, RG070 revised; migrating a header card moves
the row AND the column together). The diagonal (row == col, no
self-relationship RG035) and the lower triangle are dimmed and
non-interactive: exactly ONE active cell per agent pair (row < col). This also
settles the combinatorial question: with RG035 the displayed relationships are
bounded by N(N-1)/2 for N agents, and the matrix size depends on N only. An
active cell hosts a MatrixRelationshipCard (border #E06666 = the Pivot/Condition
color, label = relationship type, tooltip = type + pair + anchor block + note,
RG054); at most one card per cell (derived state at the selected block, RG069 +
RG035). There is NO left click on cells anymore: creation/edition/deletion go
through the right-click context menu only (RG055) - empty cell -> "New..."
(dialog pre-filled with the pair + anchor block), filled cell -> Edit/Delete of
that relationship + "View in Journeys view" (FN032); the context menu is also
active on the agent header cards (agent_context_menu_requested).
"""
import logging
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsLineItem, QFrame,
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QEvent
from PySide6.QtGui import QColor, QBrush, QPen, QPainter, QPainterPath, QPainterPathStroker

from core.models.data_model import NarrativeMap, Project
from core.models.view_model import ProjectLayout
from core.services.journey_filter_service import JourneyFilterService
from core.services.agent_filter_service import AgentFilterService
from core.services.relationship_service import RelationshipService
from ui.nodes.matrix_agent_card import MatrixAgentCard
from ui.nodes.matrix_relationship_card import MatrixRelationshipCard
from ui.widgets.filters_side_panel import (
    FiltersSidePanel, SidePanelSplitter, PANEL_WIDTH_PX, SEPARATOR_HEIGHT_PX,
)
from config.config_loader import get as _get_config
from ui.utils import theme

# TSK33: the side panel is the shared FiltersSidePanel; its width comes from
# the shared side_panel_width_px key (fallback relationships_view_panel_width_px)
_PANEL_WIDTH = PANEL_WIDTH_PX  # alias kept for the offscreen tests
_CELL_SIZE = int(_get_config("relationships_view_cell_size_px", 100))  # square cells (TSK29)
_BG_PRIMARY = _get_config("bg_primary", theme.BG_PRIMARY)
_GRID_MINOR_COLOR = _get_config("grid_minor_color", "#333333")
_GRID_MAJOR_COLOR = _get_config("grid_major_color", "#4A4A4A")
_BORDER_COLOR = _get_config("border_color", "#383838")
_CELL_HIT_WIDTH = _get_config("journeys_view_hit_area_width_px", 12.0)
_CELL_MARGIN = 2.0
# TSK30: scene anchored on the top-left corner, growing rightwards/downwards only
_SCENE_MIN_SIZE = 4000
# TSK32: the Relationship card materialized inside an active (upper-triangle) cell
_REL_CARD_W = MatrixRelationshipCard.WIDTH
_REL_CARD_H = MatrixRelationshipCard.HEIGHT
# TSK31 (3.1): separator between the filter zone and the block list
_SEPARATOR_HEIGHT = SEPARATOR_HEIGHT_PX  # alias kept for the offscreen tests
_CARD_W = MatrixAgentCard.WIDTH
_CARD_H = MatrixAgentCard.HEIGHT
_CARD_OFF_X = (_CELL_SIZE - _CARD_W) / 2   # 10 px at C=100 -> 20 px between adjacent cards
_CARD_OFF_Y = (_CELL_SIZE - _CARD_H) / 2   # 30 px at C=100
_CELLS_LEFT = _CELL_SIZE    # cells area starts after the row-header column
_CELLS_TOP = _CELL_SIZE     # ... and after the column-header row

logger = logging.getLogger(__name__)


class _MatrixCell(QGraphicsRectItem):
    """One matrix cell (row, col). TSK32 (upper-triangle matrix): only cells
    with row < col are active - the diagonal (row == col, no self-relationship
    RG035) and the lower triangle are dimmed and non-interactive. An active
    cell with a relationship at the selected block hosts a
    MatrixRelationshipCard (centered child item); the cell itself stays
    transparent (the matrix lines are the background grid lines, TSK31)."""

    def __init__(self, row: int, col: int):
        super().__init__(0, 0, _CELL_SIZE - 2 * _CELL_MARGIN, _CELL_SIZE - 2 * _CELL_MARGIN)
        self.row = row
        self.col = col
        self.clickable = True
        self.dimmed = False
        self.card: Optional[MatrixRelationshipCard] = None
        self.setPos(_CELLS_LEFT + col * _CELL_SIZE + _CELL_MARGIN,
                    _CELLS_TOP + row * _CELL_SIZE + _CELL_MARGIN)
        self.setZValue(0)

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(_CELL_HIT_WIDTH)
        path = QPainterPath()
        path.addRect(self.rect())
        return stroker.createStroke(path).united(path)

    def set_content(self, rel, tooltip: str, dimmed: bool):
        """TSK32: host (or remove) the Relationship card of this cell."""
        self.dimmed = dimmed
        if rel is None:
            if self.card is not None:
                # TSK34 (retour 3): a QGraphicsItem is NOT a QObject (no
                # deleteLater - AttributeError) - remove the card from the
                # scene instead (same pattern as the grid lines)
                scene = self.scene()
                if scene is not None:
                    scene.removeItem(self.card)
                self.card = None
        else:
            if self.card is None:
                self.card = MatrixRelationshipCard(rel.typ)
                self.card.setParentItem(self)
                self.card.setPos((self.rect().width() - _REL_CARD_W) / 2,
                                 (self.rect().height() - _REL_CARD_H) / 2)
                self.card.setZValue(1)
            self.card.set_relationship(rel.id, rel.typ, tooltip)
            self.card.setOpacity(JourneyFilterService.filter_opacity() if dimmed else 1.0)
        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        # TSK31 (2.3): the cell is transparent (no fill, no border) - the
        # background grid lines show through; only a dim overlay when the cell
        # is inactive (diagonal/lower triangle) or outside the filter (TSK32)
        if self.dimmed:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(self.rect())


class _GridLineItem(QGraphicsLineItem):
    """Non-interactive grid line (TSK30, planoscript pattern): painted normally
    but invisible to hit-testing (empty shape), so it never blocks clicks on
    the cards and cells. boundingRect() covers the painted line, otherwise the
    scene index would drop the item as soon as the view scrolls past it."""

    def shape(self):
        return QPainterPath()

    def boundingRect(self):
        line = self.line()
        left = min(line.x1(), line.x2())
        top = min(line.y1(), line.y2())
        right = max(line.x1(), line.x2())
        bottom = max(line.y1(), line.y2())
        return QRectF(left - 1, top - 1, right - left + 2, bottom - top + 2)


class _MatrixGraphicsView(QGraphicsView):
    """Graphics view of the matrix; mouse handling delegates to the workspace
    (card drag constrained to its axis, cell click, context menu)."""

    def __init__(self, workspace: 'RelationshipsWorkspace'):
        super().__init__()
        self._workspace = workspace
        self.setFrameShape(QFrame.NoFrame)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # TSK30: matrix anchored to the top-left corner (not centered), the
        # workspace extends rightwards/downwards only; scrollbars always on
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setMinimumSize(0, 0)  # never raise the window minimum size (TSK30 3.3)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        # TSK31 (2.5): same scrollbar appearance/behavior as the "Journeys" view
        self.setStyleSheet(theme.WORKSPACE_STYLESHEET)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._dragged_card = None

    # TSK36 (session 11, option 2 validated by TSC): NO dots in the background -
    # the per-cell center dot (TSK31 2.4) and the agents-view dot field (TSK36
    # option 1, tested then rejected) are both removed; the default
    # drawBackground fills the background brush (bg_primary) and the cell grid
    # lines (_GridLineItem) remain.

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
            if cell is not None:
                # TSK32: no left-click action on the cells - creation/edition
                # only via the right-click context menu (RG055)
                self._workspace.scene.clearSelection()
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
        # TSK31 (2.1): QContextMenuEvent exposes pos()/globalPos() (QPoint),
        # not position() - avoid AttributeError on right click
        pos = self.mapToScene(event.pos())
        card = self._workspace._card_at(pos)
        if card is not None:
            # TSK32: the context menu is also active on the agent header cards
            self._workspace.agent_context_menu_requested.emit(
                card.entity.id, self.viewport().mapToGlobal(event.pos()))
            event.accept()
            return
        cell = self._workspace._cell_at(pos)
        if cell is not None and cell.clickable and not cell.dimmed:
            self._workspace.context_menu_requested.emit(
                cell.row, cell.col, self.viewport().mapToGlobal(event.pos()))
            event.accept()
            return
        super().contextMenuEvent(event)


class RelationshipsWorkspace(QWidget):
    """Workspace of the "Relationships" view: agent x agent matrix + side panel."""

    anchor_block_selected = Signal(int)              # block id (side panel list)
    journey_filter_requested = Signal(object)        # journey id or None (All journeys); mirror of Display > Journey (TSK30 4.1)
    agent_filter_requested = Signal(object)          # agent id or None
    context_menu_requested = Signal(int, int, object)  # row, col, global QPoint (right click on an active cell, RG055)
    agent_context_menu_requested = Signal(int, object)  # agent id, global QPoint (right click on a header card, TSK32)
    axis_order_changed = Signal(list)                # shared row/column order (RG070 revised TSK32)
    workspace_modified = Signal()

    # TSK33: the side panel (FiltersSidePanel) owns the filter/anchor state;
    # these delegates keep the historical attribute names used by the matrix
    # logic and the tests
    @property
    def _block_ids(self) -> List[int]:
        return self.panel.block_ids

    @property
    def _anchor_block_id(self) -> Optional[int]:
        return self.panel.get_anchor_block_id()

    @_anchor_block_id.setter
    def _anchor_block_id(self, value: Optional[int]):
        self.panel._set_anchor_block_silent(value)

    @property
    def _journey_filter_active(self) -> bool:
        return self.panel.journey_filter_active

    @property
    def _agent_filter_agent_id(self) -> Optional[int]:
        return self.panel.agent_filter_agent_id

    # TSK32: a single shared order for rows AND columns (upper-triangle
    # matrix); _row_order/_col_order stay as read-only aliases (tests)
    @property
    def _row_order(self) -> List[int]:
        return self._order

    @property
    def _col_order(self) -> List[int]:
        return self._order

    def __init__(self, project: Project, narrative_map: NarrativeMap,
                 info_bar=None, main_window=None):
        super().__init__()
        self.project = project
        self.narrative_map = narrative_map
        self.info_bar = info_bar
        self._main_window = main_window
        self._order: List[int] = []         # agent ids, shared rows+columns order (RG070 revised TSK32)
        self._row_cards: Dict[int, MatrixAgentCard] = {}
        self._col_cards: Dict[int, MatrixAgentCard] = {}
        self._cells: Dict[Tuple[int, int], _MatrixCell] = {}
        self._build_ui()  # creates self.panel (FiltersSidePanel), owner of the filter/anchor state

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.scene = QGraphicsScene()
        self.view = _MatrixGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setBackgroundBrush(QBrush(QColor(_BG_PRIMARY)))
        # TSK30: redraw the grid over the newly visible area on scroll
        self.view.horizontalScrollBar().valueChanged.connect(self._draw_grid)
        self.view.verticalScrollBar().valueChanged.connect(self._draw_grid)
        # TSK33: the side panel is the shared FiltersSidePanel (block list
        # shown here); SidePanelSplitter pins the panel slot to the panel
        # width on resize (TSK31 3.2 - no gray strip on the right)
        self.panel = FiltersSidePanel(project=self.project, narrative_map=self.narrative_map,
                                      show_block_list=True)
        self.panel.journey_filter_requested.connect(self.journey_filter_requested)
        self.panel.agent_filter_requested.connect(self.agent_filter_requested)
        self.panel.anchor_block_selected.connect(self._on_panel_anchor_selected)
        # historical attribute names kept as aliases (matrix logic + tests)
        self.journey_combo = self.panel.journey_combo
        self.agent_combo = self.panel.agent_combo
        self.block_list = self.panel.block_list
        self._splitter = SidePanelSplitter(self.view, self.panel, parent=self)
        layout.addWidget(self._splitter)

    def _on_panel_anchor_selected(self, block_id: int):
        self._rebuild_cells()
        self.anchor_block_selected.emit(block_id)

    # ------------------------------------------------------------------
    # Populate / refresh
    # ------------------------------------------------------------------
    def populate(self, project: Project, narrative_map: NarrativeMap,
                 project_layout: Optional[ProjectLayout] = None):
        """Fill the view from the model; the shared row/column order comes from
        the saved project layout (RG070 revised TSK32), new agents appended
        alphabetically (label, id)."""
        self.project = project
        self.narrative_map = narrative_map
        self.panel.set_data(project, narrative_map)  # TSK33
        agents = list(project.agent)
        saved = project_layout.relationships_view_agent_order if project_layout else []
        self._order = RelationshipService.resolve_axis_order(agents, saved)
        self.panel.refresh()  # TSK33: combos + block list are rebuilt by the panel
        start = next((b for b in narrative_map.block if b.typ == "Start"), None)  # RG025/RG068
        self._anchor_block_id = start.id if start is not None else (
            narrative_map.block[0].id if narrative_map.block else None)
        self._relayout()
        self._rebuild_cells()

    def refresh(self):
        """Recompute from the model (agents/blocks/relationships changed);
        keeps current orders, anchor block and filters."""
        agents = list(self.project.agent)
        known = {a.id for a in agents}
        self._order = [i for i in self._order if i in known] + \
            [a.id for a in sorted(agents, key=lambda a: (a.lb, a.id)) if a.id not in self._order]
        self.panel.set_data(self.project, self.narrative_map)  # TSK33
        self.panel.refresh()
        if self._anchor_block_id is None or self._anchor_block_id not in self._block_ids:
            start = next((b for b in self.narrative_map.block if b.typ == "Start"), None)
            self._anchor_block_id = start.id if start is not None else (
                self._block_ids[0] if self._block_ids else None)
        self._relayout()
        self._rebuild_cells()

    def collect_project_layout(self, layout: ProjectLayout):
        """RG070 (revised session 10, TSK32): persist the single shared
        row/column order at project level."""
        layout.relationships_view_agent_order = list(self._order)

    def get_anchor_block_id(self) -> Optional[int]:
        return self.panel.get_anchor_block_id()  # TSK33

    def agent_id_at_row(self, row: int) -> Optional[int]:
        # TSK32: rows and columns share the same order
        return self._order[row] if 0 <= row < len(self._order) else None

    def agent_id_at_col(self, col: int) -> Optional[int]:
        return self._order[col] if 0 <= col < len(self._order) else None

    # ------------------------------------------------------------------
    # Scene geometry / layout
    # ------------------------------------------------------------------
    def _card_at(self, pos: QPointF):
        # TSK30 (3.5): shape() is in item-local coordinates, map the scene pos first
        for card in list(self._row_cards.values()) + list(self._col_cards.values()):
            if card.shape().contains(card.mapFromScene(pos)):
                return card
        return None

    def _cell_at(self, pos: QPointF):
        for cell in self._cells.values():
            if cell.shape().contains(cell.mapFromScene(pos)):
                return cell
        return None

    def _relayout(self):
        """(Re)create and position header cards and cells from the single
        shared order (TSK32: rows and columns carry the same agents).
        TSK39 (2.3): also REMOVE the cards/cells of agents that are no longer
        in the order (e.g. deleted agent) - refresh() prunes the order but the
        scene must be pruned too, otherwise a ghost card stays visible and
        draggable."""
        agents = {a.id: a for a in self.project.agent}
        # TSK39 (2.3): remove the header cards of agents no longer in the order
        order_set = set(self._order)
        for cards in (self._row_cards, self._col_cards):
            for aid in [aid for aid in cards if aid not in order_set]:
                self.scene.removeItem(cards[aid])
                del cards[aid]
        # TSK39 (2.3): remove the cells outside the current order
        n = len(self._order)
        for key in [k for k in self._cells if k[0] >= n or k[1] >= n]:
            cell = self._cells.pop(key)
            if cell.card is not None:
                self.scene.removeItem(cell.card)
                cell.card = None
            self.scene.removeItem(cell)
        # row header cards (left column)
        for i, aid in enumerate(self._order):
            card = self._row_cards.get(aid)
            if card is None:
                card = MatrixAgentCard(agents[aid], 'row')
                self.scene.addItem(card)
                self._row_cards[aid] = card
            card.setPos(_CARD_OFF_X, _CELLS_TOP + i * _CELL_SIZE + _CARD_OFF_Y)
        # column header cards (top row) - same order, same index (TSK32)
        for j, aid in enumerate(self._order):
            card = self._col_cards.get(aid)
            if card is None:
                card = MatrixAgentCard(agents[aid], 'column')
                self.scene.addItem(card)
                self._col_cards[aid] = card
            card.setPos(_CELLS_LEFT + j * _CELL_SIZE + _CARD_OFF_X, _CARD_OFF_Y)
        # cells
        for i in range(len(self._order)):
            for j in range(len(self._order)):
                cell = self._cells.get((i, j))
                if cell is None:
                    cell = _MatrixCell(i, j)
                    self.scene.addItem(cell)
                    self._cells[(i, j)] = cell
        # scene rect: anchored on the top-left corner, grows rightwards/downwards
        # only, at least _SCENE_MIN_SIZE so the scrollbars stay usable (TSK30)
        w = _CELLS_LEFT + len(self._order) * _CELL_SIZE + _CELL_SIZE
        h = _CELLS_TOP + len(self._order) * _CELL_SIZE + _CELL_SIZE
        self.scene.setSceneRect(0, 0, max(w, _SCENE_MIN_SIZE), max(h, _SCENE_MIN_SIZE))
        self._draw_grid()

    def _draw_grid(self):
        """Background grid over the WHOLE visible area (TSK30 3.6), snapped on
        the cell grid; non-interactive lines (_GridLineItem)."""
        for item in list(self.scene.items()):
            if getattr(item, '_is_grid_line', False):
                self.scene.removeItem(item)
        rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        y1 = rect.top() - _CELL_SIZE
        y2 = rect.bottom() + _CELL_SIZE
        x1 = rect.left() - _CELL_SIZE
        x2 = rect.right() + _CELL_SIZE
        start_x = int(x1 - (x1 % _CELL_SIZE))
        for x in range(start_x, int(x2) + _CELL_SIZE, _CELL_SIZE):
            line = _GridLineItem(x, y1, x, y2)
            line.setPen(QPen(QColor(_GRID_MAJOR_COLOR if round(x / _CELL_SIZE) % 4 == 0 else _GRID_MINOR_COLOR), 1))
            line.setZValue(-2)
            line._is_grid_line = True
            self.scene.addItem(line)
        start_y = int(y1 - (y1 % _CELL_SIZE))
        for y in range(start_y, int(y2) + _CELL_SIZE, _CELL_SIZE):
            line = _GridLineItem(x1, y, x2, y)
            line.setPen(QPen(QColor(_GRID_MAJOR_COLOR if round(y / _CELL_SIZE) % 4 == 0 else _GRID_MINOR_COLOR), 1))
            line.setZValue(-2)
            line._is_grid_line = True
            self.scene.addItem(line)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # TSK33: the SidePanelSplitter pins the panel slot itself (TSK31 3.2)
        self._draw_grid()

    def showEvent(self, event):
        super().showEvent(event)
        # TSK34 (retour 2): the grid is redrawn on resize/scroll, but a page
        # hidden at populate time never received a resize event -> redraw the
        # grid over the whole visible area when the tab is first shown
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
        agents = {a.id: a for a in self.project.agent}
        blocks = {b.id: b for b in nm.block}
        anchor = blocks.get(self._anchor_block_id) if self._anchor_block_id is not None else None
        for (i, j), cell in self._cells.items():
            ai = self.agent_id_at_row(i)
            aj = self.agent_id_at_col(j)
            # TSK32 (upper-triangle matrix): only cells with row < col are
            # active - the diagonal (no self-relationship, RG035) and the lower
            # triangle are dimmed and non-interactive; exactly ONE active cell
            # per agent pair
            if i >= j or ai is None or aj is None:
                cell.set_content(None, "", dimmed=True)
                cell.clickable = False
                cell.setEnabled(False)
                continue
            rel = None
            if self._anchor_block_id is not None:
                rel = RelationshipService.pair_state_at_block(nm, ai, aj, self._anchor_block_id)
            dimmed = False
            clickable = True
            if rel is not None and rel.id not in vis_rel:
                dimmed = True
                clickable = False  # RG048/RG063: outside the filter, non-interactive
            if filtered_agent is not None and filtered_agent not in (ai, aj):
                clickable = False  # RG069: creation forbidden for uninvolved agents
            tooltip = ""
            if rel is not None:
                tooltip = f"{rel.typ}\n{agents[ai].lb} — {agents[aj].lb}"
                if anchor is not None:
                    tooltip += f"\nAnchor: {anchor.lb} ({anchor.typ})"
                if rel.note:
                    tooltip += f"\n{rel.note}"
            cell.set_content(rel, tooltip, dimmed)
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
        # TSK39 (2.3): a card whose agent is no longer in the order (deleted
        # agent) is not reorderable - ignore the release (avoids ValueError
        # in _reorder's order.index)
        if card.entity.id not in self._order:
            return
        # TSK32: one shared order - the row and the column axes follow together
        if card.kind == 'column':
            target = round((scene_pos.x() - _CELLS_LEFT - _CARD_OFF_X) / _CELL_SIZE)
        else:
            target = round((scene_pos.y() - _CELLS_TOP - _CARD_OFF_Y) / _CELL_SIZE)
        self._reorder(self._order, target, card.entity.id)
        self._relayout()
        self._rebuild_cells()
        self.axis_order_changed.emit(list(self._order))
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
    # TSK33: the combos and the block list are rebuilt by the side panel
    # (FiltersSidePanel); the workspace only recomputes the matrix
    def set_journey_filter_active(self, active: bool):
        self.panel.set_journey_filter_active(active)
        self._rebuild_cells()

    def set_agent_filter(self, agent_id: Optional[int]):
        self.panel.set_agent_filter(agent_id)
        self._rebuild_cells()

    def set_anchor_block(self, block_id: int):
        """Select the given block in the panel and recompute the matrix (RG069)."""
        self.panel.set_anchor_block(block_id)
        self._rebuild_cells()
