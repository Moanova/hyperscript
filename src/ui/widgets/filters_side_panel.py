# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : filters_side_panel.py
# Version      : 1
# Date         : 2026-11-20
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Filters side panel shared by the map views (TSK33, session 10).

The "Relationships" view hosts FiltersSidePanel(show_block_list=True): the
Journey + Agent filter zones, a separator, then the ordered block list used
to follow the relationships (RG069). The "Journeys" view hosts the SAME panel
with show_block_list=False: the Journey + Agent filter zones only, the area
below the filters stays empty.

The panel NEVER writes the business model (RG058): the combos emit
journey_filter_requested / agent_filter_requested and the MainWindow applies
the use cases / filter state, exactly like the Display menu (TSK30 4.1:
choosing a journey in the panel activates it, FN026, and enables the filter,
FN029). The filter state is owned by the MainWindow and pushed back through
set_journey_filter_active / set_agent_filter, so the combos always mirror
the Display menu and the other view's panel.
"""
import logging
from typing import List, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QComboBox, QListWidget, QListWidgetItem,
    QFrame, QLabel,
)
from PySide6.QtCore import Qt, Signal

from core.models.data_model import NarrativeMap, Project
from core.services.journey_filter_service import JourneyFilterService
from core.services.agent_filter_service import AgentFilterService
from core.services.relationship_service import RelationshipService
from config.config_loader import get as _get_config
from ui.utils import theme

# TSK33: shared width of the side panels (fallback on the historical
# relationships_view_panel_width_px key)
PANEL_WIDTH_PX = int(_get_config("side_panel_width_px",
                                 _get_config("relationships_view_panel_width_px", 260)))
SEPARATOR_HEIGHT_PX = int(_get_config("relationships_view_separator_height_px", 2))
_ALL_JOURNEYS_LABEL = _get_config("journey_list_all_label", "All journeys")
_ALL_AGENTS_LABEL = _get_config("agent_list_all_label", "All agents")
_GRID_MAJOR_COLOR = _get_config("grid_major_color", "#4A4A4A")
_BG_SURFACE = _get_config("bg_surface", theme.BG_SURFACE)
_BORDER_COLOR = _get_config("border_color", theme.BORDER_COLOR)

logger = logging.getLogger(__name__)


class FiltersSidePanel(QWidget):
    """Side panel of a map view: Journey + Agent filter combos (mirrors of the
    Display menu), then - only when show_block_list=True ("Relationships"
    view) - a separator and the ordered block list (RG069)."""

    journey_filter_requested = Signal(object)   # journey id or None (All journeys); mirror of Display > Journey (TSK30 4.1)
    agent_filter_requested = Signal(object)     # agent id or None
    anchor_block_selected = Signal(int)         # block id (block list, "Relationships" view only)

    def __init__(self, project: Optional[Project] = None,
                 narrative_map: Optional[NarrativeMap] = None,
                 show_block_list: bool = True, parent=None):
        super().__init__(parent)
        self._project = project
        self._narrative_map = narrative_map
        self.show_block_list = show_block_list
        self.journey_filter_active = False        # pushed by MainWindow (RG047: off by default)
        self.agent_filter_agent_id: Optional[int] = None
        self._block_ids: List[int] = []
        self._anchor_block_id: Optional[int] = None
        self._updating_combos = False
        self._updating_blocks = False
        self._build_ui()

    def _build_ui(self):
        self.setFixedWidth(PANEL_WIDTH_PX)
        # TSK31 (3.2): dark-themed panel content (labels, combos, list, scrollbars)
        self.setStyleSheet(theme.SIDE_PANEL_STYLESHEET)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Journey"))
        self.journey_combo = QComboBox()
        self.journey_combo.currentIndexChanged.connect(self._on_journey_combo)
        layout.addWidget(self.journey_combo)
        layout.addWidget(QLabel("Agent"))
        self.agent_combo = QComboBox()
        self.agent_combo.currentIndexChanged.connect(self._on_agent_combo)
        layout.addWidget(self.agent_combo)
        self.block_list: Optional[QListWidget] = None
        if self.show_block_list:
            # TSK30 (3.8) + TSK31 (3.1): separator between the filter zone and the block list
            separator = QFrame()
            separator.setFixedHeight(SEPARATOR_HEIGHT_PX)
            separator.setStyleSheet(f"background-color: {_GRID_MAJOR_COLOR}; border: none;")
            layout.addWidget(separator)
            layout.addWidget(QLabel("Blocks"))
            self.block_list = QListWidget()
            self.block_list.currentRowChanged.connect(self._on_block_selected)
            # TSK31 (3.2): the block list scrollbar is always visible, styled like
            # the "Journeys" view scrollbars - and only in the list zone
            self.block_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.block_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            layout.addWidget(self.block_list, stretch=1)
        else:
            # TSK33: map views without the relationship block list ("Journeys"):
            # the area below the filters stays empty
            layout.addStretch(1)

    # ------------------------------------------------------------------
    # Data / refresh
    # ------------------------------------------------------------------
    def set_data(self, project: Project, narrative_map: NarrativeMap):
        self._project = project
        self._narrative_map = narrative_map

    def refresh(self):
        """Rebuild the combos and the block list from the model; keeps the
        current filters and anchor block."""
        self.rebuild_filter_combos()
        self.rebuild_block_list()

    @property
    def block_ids(self) -> List[int]:
        return self._block_ids

    def get_anchor_block_id(self) -> Optional[int]:
        return self._anchor_block_id

    def set_anchor_block(self, block_id: int):
        """Select the given block in the list (programmatic; no signal)."""
        if block_id in self._block_ids:
            self._anchor_block_id = block_id
            self._sync_block_list_selection()

    def _set_anchor_block_silent(self, block_id: Optional[int]):
        self._anchor_block_id = block_id
        self._sync_block_list_selection()

    # ------------------------------------------------------------------
    # Filters (pushed by MainWindow; the panel zones only request changes)
    # ------------------------------------------------------------------
    def set_journey_filter_active(self, active: bool):
        self.journey_filter_active = active
        self.rebuild_filter_combos()
        self.rebuild_block_list()

    def set_agent_filter(self, agent_id: Optional[int]):
        self.agent_filter_agent_id = agent_id
        self.rebuild_filter_combos()
        self.rebuild_block_list()

    def rebuild_filter_combos(self):
        self._updating_combos = True
        try:
            nm = self._narrative_map
            self.journey_combo.clear()
            self.journey_combo.addItem(_ALL_JOURNEYS_LABEL, None)
            for j in nm.journey:
                self.journey_combo.addItem(j.lb, j.id)
            if self.journey_filter_active:
                active = nm.get_active_journey()
                idx = self.journey_combo.findData(active.id if active else None)
                self.journey_combo.setCurrentIndex(idx if idx >= 0 else 0)
            else:
                self.journey_combo.setCurrentIndex(0)
            self.agent_combo.clear()
            self.agent_combo.addItem(_ALL_AGENTS_LABEL, None)
            for a in sorted(self._project.agent, key=lambda a: (a.lb, a.id)):
                self.agent_combo.addItem(f"{a.lb} ({a.typ})", a.id)
            idx = self.agent_combo.findData(self.agent_filter_agent_id)
            self.agent_combo.setCurrentIndex(idx if idx >= 0 else 0)
        finally:
            self._updating_combos = False

    def _on_journey_combo(self, index):
        if self._updating_combos:
            return
        # TSK30 (4.1): emit the chosen journey id (None = "All journeys") so the
        # MainWindow can activate it, like Display > Journey does
        self.journey_filter_requested.emit(self.journey_combo.itemData(index))

    def _on_agent_combo(self, index):
        if self._updating_combos:
            return
        self.agent_filter_requested.emit(self.agent_combo.itemData(index))

    # ------------------------------------------------------------------
    # Block list (RG069: min rank across all journeys, ties by id, restricted
    # to the blocks visible under the active filters - RG064)
    # ------------------------------------------------------------------
    def rebuild_block_list(self):
        if self.block_list is None:  # TSK33: no block list in the "Journeys" view
            self._block_ids = []
            return
        self._updating_blocks = True
        try:
            nm = self._narrative_map
            visible = set(RelationshipService.ordered_anchor_block_ids(nm))
            if self.journey_filter_active:
                active = nm.get_active_journey()
                visible &= JourneyFilterService.visible_block_ids(nm, active.id if active else None)
            if self.agent_filter_agent_id is not None:
                visible &= AgentFilterService.visible_block_ids(nm, self.agent_filter_agent_id)
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
        if self.block_list is None:
            return
        if self._anchor_block_id in self._block_ids:
            row = self._block_ids.index(self._anchor_block_id)
            self.block_list.blockSignals(True)
            self.block_list.setCurrentRow(row)
            self.block_list.blockSignals(False)

    def _on_block_selected(self, row):
        if self.block_list is None or self._updating_blocks or not (0 <= row < len(self._block_ids)):
            return
        bid = self._block_ids[row]
        self._anchor_block_id = bid
        self.anchor_block_selected.emit(bid)


class SidePanelSplitter(QSplitter):
    """Horizontal splitter: map view + fixed-width FiltersSidePanel. The panel
    slot is pinned to the panel width on resize (TSK31 3.2 pattern: no exposed
    splitter background strip on the right of the panel)."""

    def __init__(self, view: QWidget, panel: FiltersSidePanel, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._panel = panel
        # TSK31 (3.2): dark splitter (handle + any exposed background)
        self.setStyleSheet(
            f"QSplitter {{ background-color: {_BG_SURFACE}; }}"
            f"QSplitter::handle {{ background-color: {_BORDER_COLOR}; }}")
        self.addWidget(view)
        self.addWidget(panel)
        self.setStretchFactor(0, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        handle = self.handleWidth()
        self.setSizes([max(0, self.width() - PANEL_WIDTH_PX - handle), PANEL_WIDTH_PX])
