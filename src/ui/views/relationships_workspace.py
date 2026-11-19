# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : relationships_workspace.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Relationships workspace (TSK27): the widget of the "Relationships" tab.

Mockup adopted session 06 (04_interface section 6, SU012/FN036, RG069/RG070):
- central area: an agent x agent matrix (read-only QTableWidget, movable row
  and column headers - RG070). Cell (A, B) shows the type of the pair's state
  at the selected block: the relationship anchored to the last block of rank
  <= the selected block's rank (derived data, RG069 - RelationshipService.
  pair_state_at_block). The matrix is symmetric (non-directed, RG035) and is
  recomputed on every selected-block change.
- right side panel: two filter zones (journey, agent - mirrors of the Display
  menu, same actions, state owned by MainWindow) then the block list, top to
  bottom by minimum rank across all journeys (ties by id - RG069), restricted
  to the blocks visible under the active filters (intersection RG064).
- default selected block: the Start block (RG068); when arriving from a block
  selected in "Journeys", that block if it belongs to the active filter,
  otherwise the Start (RG069).
- filters (RG048/RG063/RG064): relationships whose anchor block is outside the
  filter are dimmed and non-interactive; with the agent filter active, the
  uninvolved agents are dimmed and creating a relationship involving them is
  forbidden (cells of a pair not involving the filtered agent are disabled).

The workspace NEVER writes the business model (RG058): it emits signals and
the MainWindow applies the use cases. The axis order is persisted at project
level (ProjectLayout.relationships_axis_order, layouts/project.json, RG070).
"""
import logging
from typing import List, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QComboBox, QListWidget, QListWidgetItem, QLabel,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from core.models.data_model import NarrativeMap, Project
from core.models.view_model import ProjectLayout
from core.services.journey_filter_service import JourneyFilterService
from core.services.agent_filter_service import AgentFilterService
from core.services.relationship_service import RelationshipService
from config.config_loader import get as _get_config
from ui.utils import theme

_PANEL_WIDTH = int(_get_config("relationships_view_panel_width_px", 260))
_CELL_SIZE = int(_get_config("relationships_view_cell_size_px", 64))
_TYPE_COLORS = _get_config("relationship_type_colors", {})
_FALLBACK_TYPE_COLOR = _get_config("block_scene_color", "#E5C07B")
_ALL_JOURNEYS_LABEL = _get_config("journey_list_all_label", "All journeys")
_ALL_AGENTS_LABEL = _get_config("agent_list_all_label", "All agents")

logger = logging.getLogger(__name__)


class RelationshipsWorkspace(QWidget):
    """Workspace of the "Relationships" view: agent x agent matrix + side panel."""

    # Emitted when the user selects a block in the side panel list (RG069)
    anchor_block_selected = Signal(int)  # block id

    # Filter zones are mirrors of the Display menu: they only request the
    # change; MainWindow owns the filter state and pushes it back (RG047)
    journey_filter_requested = Signal(bool)   # True = filter active
    agent_filter_requested = Signal(object)   # agent id or None

    # Emitted on right-click on a matrix cell (RG055): row, col, global QPoint
    context_menu_requested = Signal(int, int, object)

    # Emitted when the user moves a row/column header (RG070): new axis order
    axis_order_changed = Signal(list)  # agent ids, visual order

    # Emitted when the visual layout changed (axis order moved - persisted at
    # project level on save, RG070)
    workspace_modified = Signal()

    def __init__(self, project: Project, narrative_map: NarrativeMap,
                 info_bar=None, main_window=None):
        super().__init__()
        self.project = project
        self.narrative_map = narrative_map
        self.info_bar = info_bar
        self._main_window = main_window
        self._axis_order: List[int] = []       # agent ids, visual order (RG070)
        self._block_ids: List[int] = []        # block ids shown in the panel list
        self._anchor_block_id: Optional[int] = None
        self._journey_filter_active = False
        self._agent_filter_agent_id: Optional[int] = None
        self._syncing_headers = False
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

        self.matrix = QTableWidget()
        self.matrix.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.matrix.setSelectionMode(QAbstractItemView.SingleSelection)
        self.matrix.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.matrix.horizontalHeader().setSectionsMovable(True)
        self.matrix.verticalHeader().setSectionsMovable(True)
        self.matrix.horizontalHeader().sectionMoved.connect(self._on_section_moved)
        self.matrix.verticalHeader().sectionMoved.connect(self._on_section_moved)
        self.matrix.setContextMenuPolicy(Qt.CustomContextMenu)
        self.matrix.customContextMenuRequested.connect(self._on_matrix_context_menu)
        self.matrix.setStyleSheet(
            f"QTableWidget {{ background-color: {_get_config('bg_primary', theme.BG_PRIMARY)}; "
            f"color: {_get_config('text_primary', theme.TEXT_PRIMARY)}; gridline-color: {_get_config('border_color', '#383838')}; }}"
            f"QHeaderView::section {{ background-color: {_get_config('bg_surface', theme.BG_SURFACE)}; "
            f"color: {_get_config('text_primary', theme.TEXT_PRIMARY)}; border: 1px solid {_get_config('border_color', '#383838')}; }}"
        )
        splitter.addWidget(self.matrix)

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
        """Fill the view from the model; axis order from the saved project
        layout (RG070), new agents appended alphabetically (label, then id)."""
        self.project = project
        self.narrative_map = narrative_map
        saved = list(project_layout.relationships_axis_order) if project_layout else []
        agent_ids = {a.id for a in project.agent}
        labels = {a.id: a.lb for a in project.agent}
        order = [i for i in saved if i in agent_ids]
        order += sorted((a for a in agent_ids if a not in order),
                        key=lambda aid: (labels[aid], aid))
        self._axis_order = order
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        start = next((b for b in narrative_map.block if b.typ == "Start"), None)  # RG025/RG068
        self._anchor_block_id = start.id if start is not None else (
            narrative_map.block[0].id if narrative_map.block else None)
        self._rebuild_matrix()
        self._sync_block_list_selection()

    def refresh(self):
        """Recompute everything from the model (agents/blocks/relationships
        changed); keeps the current axis order, anchor block and filters."""
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        if self._anchor_block_id is None or self._anchor_block_id not in self._block_ids:
            start = next((b for b in self.narrative_map.block if b.typ == "Start"), None)
            self._anchor_block_id = start.id if start is not None else (
                self._block_ids[0] if self._block_ids else None)
        self._rebuild_matrix()
        self._sync_block_list_selection()

    def collect_project_layout(self, layout: ProjectLayout):
        """RG070: persist the current axis order at project level."""
        layout.relationships_axis_order = list(self._axis_order)

    def get_anchor_block_id(self) -> Optional[int]:
        return self._anchor_block_id

    def agent_id_at(self, row: int) -> Optional[int]:
        if 0 <= row < len(self._axis_order):
            return self._axis_order[row]
        return None

    # ------------------------------------------------------------------
    # Filters (pushed by MainWindow; the zones above only request changes)
    # ------------------------------------------------------------------
    def set_journey_filter_active(self, active: bool):
        self._journey_filter_active = active
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        self._rebuild_matrix()

    def set_agent_filter(self, agent_id: Optional[int]):
        self._agent_filter_agent_id = agent_id
        self._rebuild_filter_combos()
        self._rebuild_block_list()
        self._rebuild_matrix()

    def _visible_relationship_ids(self):
        """RG048/RG063/RG064: intersection of the active filters."""
        nm = self.narrative_map
        vis = set(JourneyFilterService.visible_relationship_ids(nm))
        if self._journey_filter_active:
            active = nm.get_active_journey()
            vis &= JourneyFilterService.visible_relationship_ids(
                nm, active.id if active else None)
        if self._agent_filter_agent_id is not None:
            vis &= AgentFilterService.visible_relationship_ids(nm, self._agent_filter_agent_id)
        return vis

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
    # restricted to the blocks visible under the active filters - RG064)
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
        self._rebuild_matrix()
        self.anchor_block_selected.emit(bid)

    def set_anchor_block(self, block_id: int):
        """Select the given block in the panel and recompute the matrix (RG069)."""
        if block_id in self._block_ids:
            self._anchor_block_id = block_id
            self._sync_block_list_selection()
            self._rebuild_matrix()

    # ------------------------------------------------------------------
    # Matrix
    # ------------------------------------------------------------------
    def _rebuild_matrix(self):
        agents = {a.id: a for a in self.project.agent}
        n = len(self._axis_order)
        self.matrix.setRowCount(n)
        self.matrix.setColumnCount(n)
        labels = [agents[aid].lb if aid in agents else f"#{aid}" for aid in self._axis_order]
        self.matrix.setHorizontalHeaderLabels(labels)
        self.matrix.setVerticalHeaderLabels(labels)
        for i in range(n):
            self.matrix.setRowHeight(i, _CELL_SIZE)
            self.matrix.setColumnWidth(i, _CELL_SIZE)
        dim = QBrush(QColor(_get_config("border_color", "#383838")))
        vis_rel = self._visible_relationship_ids()
        filtered_agent = self._agent_filter_agent_id
        for i, ai in enumerate(self._axis_order):
            for j, aj in enumerate(self._axis_order):
                item = QTableWidgetItem()
                if i == j:
                    item.setFlags(Qt.NoItemFlags)
                    item.setBackground(dim)
                else:
                    rel = None
                    if self._anchor_block_id is not None:
                        rel = RelationshipService.pair_state_at_block(
                            self.narrative_map, ai, aj, self._anchor_block_id)
                    if rel is not None:
                        item.setText(rel.typ)
                        color = _TYPE_COLORS.get(rel.typ, _FALLBACK_TYPE_COLOR)
                        item.setBackground(QBrush(QColor(color)))
                        item.setForeground(QBrush(QColor(_get_config("badge_text_color", "#1E1E1E"))))
                        if rel.note:
                            item.setToolTip(rel.note)
                        if rel.id not in vis_rel:
                            item.setEnabled(False)  # RG048/RG063: dimmed + non-interactive
                    # RG069: with the agent filter active, a pair not involving the
                    # filtered agent is dimmed and cannot be created
                    if filtered_agent is not None and filtered_agent not in (ai, aj):
                        item.setEnabled(False)
                self.matrix.setItem(i, j, item)
        self._dim_filtered_agents()

    def _dim_filtered_agents(self):
        """RG069: with the agent filter active, uninvolved agents are dimmed."""
        dim_color = QColor(_get_config("text_secondary", theme.TEXT_SECONDARY))
        full_color = QBrush(QColor(_get_config("text_primary", theme.TEXT_PRIMARY)))
        for i, aid in enumerate(self._axis_order):
            dimmed = self._agent_filter_agent_id is not None and aid != self._agent_filter_agent_id
            for header in (self.matrix.horizontalHeader(), self.matrix.verticalHeader()):
                header.model().setHeaderData(i, header.orientation(),
                                             dim_color if dimmed else full_color, Qt.ForegroundRole)

    # ------------------------------------------------------------------
    # Movable headers (RG070)
    # ------------------------------------------------------------------
    def _on_section_moved(self, logical, old_visual, new_visual):
        if self._syncing_headers:
            return
        self._syncing_headers = True
        try:
            sender_is_horizontal = self.sender() is self.matrix.horizontalHeader()
            other = self.matrix.verticalHeader() if sender_is_horizontal else self.matrix.horizontalHeader()
            other.moveSection(old_visual, new_visual)  # keep rows and columns in the same order
            hh = self.matrix.horizontalHeader()
            n = len(self._axis_order)
            new_order = [self._axis_order[hh.visualIndex(i)] for i in range(n)]
            # reset both headers to logical order; the matrix is rebuilt below
            for i in range(n):
                hh.setVisualIndex(i, i)
                self.matrix.verticalHeader().setVisualIndex(i, i)
        finally:
            self._syncing_headers = False
        self._axis_order = new_order
        self._rebuild_matrix()
        self.axis_order_changed.emit(list(self._axis_order))
        self.workspace_modified.emit()

    # ------------------------------------------------------------------
    # Context menu (RG055: built by MainWindow from the application menu)
    # ------------------------------------------------------------------
    def _on_matrix_context_menu(self, pos):
        index = self.matrix.indexAt(pos)
        self.context_menu_requested.emit(index.row(), index.column(),
                                         self.matrix.viewport().mapToGlobal(pos))
