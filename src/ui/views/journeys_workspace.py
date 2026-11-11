# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : journeys_workspace.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Journeys workspace (TSK11): the QGraphicsView of the "Journeys" tab.

Graph of narrative blocks (BlockNode) and transitions (Connection), adapted
from planoscript's EventsWorkspace. The workspace NEVER writes the business
model (RG058): it emits signals and the MainWindow applies the use cases.

Kept from planoscript (AGENTS.md patterns): grid drawn on the visible area
only, scene 4000x4000 dynamically extended, auto-scroll within 50 px of an
edge, single selection (RG049), hit-testing via shape() (RG053), immediate
tooltips (the workspace swallows Qt's delayed ToolTip event), temp trace for
transition creation, drag-and-drop with grid snap (RG046), dimmed + disabled
items outside the journey filter (RG048), right-click selects the item under
the cursor before the menu opens (RG055).
"""
import logging

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsItem,
    QFrame,
)
from PySide6.QtCore import Qt, QPointF, Signal, QObject, QEvent
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPainterPath

from core.models.view_model import ConnectionLayout, WorkspaceLayout
from core.models.data_model import Block, Transition
from core.services.layout_service import LayoutService
from core.services.journey_filter_service import JourneyFilterService
from ui.nodes.block_node import BlockNode
from ui.nodes.connection import Connection
from ui.utils import theme
from config.config_loader import get as _get_config

_GRID_MINOR_SIZE = _get_config("grid_minor_size", 20)
_GRID_MAJOR_SIZE = _get_config("grid_major_size", 80)
_GRID_MINOR_COLOR = _get_config("grid_minor_color", "#333333")
_GRID_MAJOR_COLOR = _get_config("grid_major_color", "#4A4A4A")
_TEMP_CONNECTION_COLOR = _get_config("temp_connection_color", theme.CONNECTION_COLOR)
_BG_PRIMARY = _get_config("bg_primary", theme.BG_PRIMARY)

logger = logging.getLogger(__name__)

# Auto-scroll margin (px) from the viewport edges while dragging (04_interface)
_SCROLL_MARGIN = 50
_SCROLL_SPEED = 20
# Distance (px) to a port for a click to count as a port click
_PORT_CLICK_THRESHOLD = 15


class JourneysWorkspace(QGraphicsView, QObject):
    """Central workspace of the "Journeys" view: blocks and transitions graph."""

    # Emitted when the user traced a transition from a source block's outgoing
    # port to a target block's incoming port (FN020); MainWindow applies the
    # CreateTransitionUseCase (RG028 validation) - the workspace never writes
    # the model (RG058)
    transition_created = Signal(object, object)  # source BlockNode, target BlockNode

    # Emitted when the visual workspace changed (block moved - FN017)
    workspace_modified = Signal()

    # Emitted on right-click after selecting the item under the cursor (RG055):
    # MainWindow builds the context menu dynamically from the application menu
    context_menu_requested = Signal(object, object)  # item (BlockNode/Connection/None), global QPoint

    def __init__(self, narrative_map=None, info_bar=None, main_window=None):
        super().__init__()

        # No frame: the default QFrame StyledPanel border was drawn in
        # light gray (bottom-left corner above the info bar)
        self.setFrameShape(QFrame.NoFrame)

        self.narrative_map = narrative_map
        self.info_bar = info_bar
        self.main_window = main_window

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(QBrush(QColor(_BG_PRIMARY)))

        self.grid_lines = []

        self.setStyleSheet(theme.WORKSPACE_STYLESHEET)
        # A plain QWidget subclass does not paint its stylesheet
        # background unless WA_StyledBackground is set
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Initial scene size 4000x4000 so the scrollbars are active by default
        self.scene_rect_margin = 200
        self.setSceneRect(0, 0, 4000, 4000)
        self._draw_grid()

        # Scrollbars always visible
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.centerOn(2000, 2000)

        self.horizontalScrollBar().valueChanged.connect(self._draw_grid)
        self.verticalScrollBar().valueChanged.connect(self._draw_grid)

        self.setAcceptDrops(True)
        # No rubber band: single selection only (RG049)
        self.setDragMode(QGraphicsView.NoDrag)

        # Transition creation mode (traced from the source's outgoing port)
        self.transition_creation_mode = False
        self.temp_connection = None
        self.source_node = None
        self.waiting_for_source = False
        self.waiting_for_target = False

        # Journey filter (FN029/RG048): purely visual state, disabled by
        # default on project opening, not persisted (RG047)
        self.journey_filter_active = False

        self.setRenderHint(QPainter.Antialiasing)

    # ------------------------------------------------------------------
    # Grid / scene geometry
    # ------------------------------------------------------------------

    def _draw_grid(self):
        """Draw grid lines only for the visible viewport area.

        Grid lines sit at z=-2, strictly below the connections (z=-1):
        same-z items are painted in insertion order, so a grid redraw
        (scroll / resize) must never overprint the transition arrows.
        """
        for line in self.grid_lines:
            if self.scene.items().count(line):
                self.scene.removeItem(line)
        self.grid_lines.clear()

        viewport_rect = self.viewport().rect()
        scene_rect = self.mapToScene(viewport_rect).boundingRect()

        margin = 100
        scene_rect.adjust(-margin, -margin, margin, margin)

        pen_main = QPen(QColor(_GRID_MINOR_COLOR))
        pen_main.setWidth(1)
        start_x = int(scene_rect.left() - (scene_rect.left() % _GRID_MINOR_SIZE))
        for x in range(start_x, int(scene_rect.right()) + _GRID_MINOR_SIZE, _GRID_MINOR_SIZE):
            line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen_main)
            line.setZValue(-2)
            self.grid_lines.append(line)
        start_y = int(scene_rect.top() - (scene_rect.top() % _GRID_MINOR_SIZE))
        for y in range(start_y, int(scene_rect.bottom()) + _GRID_MINOR_SIZE, _GRID_MINOR_SIZE):
            line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen_main)
            line.setZValue(-2)
            self.grid_lines.append(line)

        pen_sub = QPen(QColor(_GRID_MAJOR_COLOR))
        pen_sub.setWidth(1)
        start_x = int(scene_rect.left() - (scene_rect.left() % _GRID_MAJOR_SIZE))
        for x in range(start_x, int(scene_rect.right()) + _GRID_MAJOR_SIZE, _GRID_MAJOR_SIZE):
            line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen_sub)
            line.setZValue(-2)
            self.grid_lines.append(line)
        start_y = int(scene_rect.top() - (scene_rect.top() % _GRID_MAJOR_SIZE))
        for y in range(start_y, int(scene_rect.bottom()) + _GRID_MAJOR_SIZE, _GRID_MAJOR_SIZE):
            line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen_sub)
            line.setZValue(-2)
            self.grid_lines.append(line)

    def resizeEvent(self, event):
        """Redraw the grid for the new visible area."""
        super().resizeEvent(event)
        self._draw_grid()

    def _expand_scene_to_include(self, x: float, y: float, margin: int = None):
        """Dynamically expand the sceneRect to include the point (x, y)."""
        if margin is None:
            margin = self.scene_rect_margin
        new_rect = self.sceneRect()
        expanded = False
        if x - margin < new_rect.left():
            new_rect.setLeft(x - margin)
            expanded = True
        if x + margin > new_rect.right():
            new_rect.setRight(x + margin)
            expanded = True
        if y - margin < new_rect.top():
            new_rect.setTop(y - margin)
            expanded = True
        if y + margin > new_rect.bottom():
            new_rect.setBottom(y + margin)
            expanded = True
        if expanded:
            self.setSceneRect(new_rect)

    def ensure_visible(self, x: float, y: float, margin: int = 200):
        """Center the view when (x, y) falls outside the visible area (RG051)."""
        viewport_rect = self.viewport().rect()
        viewport_pos = self.mapFromScene(QPointF(x, y))
        if not viewport_rect.contains(viewport_pos):
            self.centerOn(x, y)

    def add_item_at(self, x: float, y: float, item: QGraphicsItem):
        """Add an item to the scene and expand the scene if needed."""
        self.scene.addItem(item)
        item.setPos(x, y)
        self._expand_scene_to_include(x, y)
        self.ensure_visible(x, y)

    # ------------------------------------------------------------------
    # Mouse / viewport events
    # ------------------------------------------------------------------

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        # Temp trace follows the cursor in transition creation mode
        if self.transition_creation_mode and self.temp_connection and self.source_node:
            mouse_scene_pos = self.mapToScene(event.position().toPoint())
            self._update_temp_connection(mouse_scene_pos)

        # Auto-scroll when the mouse is near a viewport edge while dragging
        if event.buttons() == Qt.LeftButton:
            viewport_rect = self.viewport().rect()
            mouse_viewport_pos = event.position().toPoint()

            if mouse_viewport_pos.x() < _SCROLL_MARGIN:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - _SCROLL_SPEED)
            elif mouse_viewport_pos.x() > viewport_rect.width() - _SCROLL_MARGIN:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + _SCROLL_SPEED)
            if mouse_viewport_pos.y() < _SCROLL_MARGIN:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - _SCROLL_SPEED)
            elif mouse_viewport_pos.y() > viewport_rect.height() - _SCROLL_MARGIN:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + _SCROLL_SPEED)

            for item in self.scene.selectedItems():
                if not (item.flags() & QGraphicsItem.ItemIsMovable):
                    continue
                item_pos = item.scenePos()
                self._expand_scene_to_include(item_pos.x(), item_pos.y())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def viewportEvent(self, event):
        """Swallow Qt's delayed automatic tooltip event.

        Item tooltips are shown instantly by the items themselves (see
        BaseNode.hoverEnterEvent / Connection.hoverEnterEvent). Letting the
        automatic mechanism run would pop a second tooltip at the cursor
        when the mouse rests.
        """
        if event.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(event)

    def mousePressEvent(self, event):
        """Single selection (RG049); in transition creation mode, port selection."""
        item = self.itemAt(event.position().toPoint())
        # RG048: an item outside the journey filter is disabled -> empty area
        if item is not None and not item.isEnabled():
            item = None

        if self.transition_creation_mode and event.button() == Qt.LeftButton:
            self._handle_port_selection(item, event)
            return

        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            if item is None:
                self._clear_all_selections()
            elif item.isEnabled() and item.isVisible():
                if item.flags() & QGraphicsItem.ItemIsSelectable:
                    self._select_item_only(item)

    # ------------------------------------------------------------------
    # Journey filter (FN029/RG048)
    # ------------------------------------------------------------------

    def _item_in_filter(self, item) -> bool:
        """True when the item belongs to the active journey under the current
        filter. Always True when the filter is disabled ("All journeys")."""
        if not self.narrative_map or not self.journey_filter_active:
            return True
        active = self.narrative_map.get_active_journey()
        journey_id = active.id if active else None
        if isinstance(item, Connection):
            return item.get_relation_id() in JourneyFilterService.visible_transition_ids(
                self.narrative_map, journey_id)
        if isinstance(item, BlockNode):
            return item.entity.id in JourneyFilterService.visible_block_ids(
                self.narrative_map, journey_id)
        return True

    def apply_journey_filter(self) -> None:
        """Recompute enabled state and opacity of every item (FN029/RG048).

        Items outside the filter are dimmed (opacity from config.json) and
        disabled (not clickable); purely visual: no model data, no layout
        change, does not mark the project as modified (RG047).
        """
        for item in self.scene.items():
            if isinstance(item, (Connection, BlockNode)):
                in_filter = self._item_in_filter(item)
                item.setEnabled(in_filter)
                self._apply_item_opacity(item)

    def _apply_item_opacity(self, item) -> None:
        """Set the dimmed opacity on top-level items only (Qt composes
        opacities down the parent chain, so children keep 1.0 and inherit)."""
        if item.parentItem() is not None:
            return
        dimmed = self.journey_filter_active and not self._item_in_filter(item)
        item.setOpacity(JourneyFilterService.filter_opacity() if dimmed else 1.0)

    def set_journey_filter_active(self, active: bool) -> None:
        """Enable/disable the journey filter and refresh the view (FN029)."""
        self.journey_filter_active = active
        self.apply_journey_filter()

    # ------------------------------------------------------------------
    # Transition creation (FN020): traced from the source's outgoing port
    # ------------------------------------------------------------------

    def enter_transition_creation_mode(self):
        """Enter transition creation mode (menu Project > Transitions > New)."""
        self.transition_creation_mode = True
        self.waiting_for_source = True
        self.waiting_for_target = False
        self.source_node = None
        self._clear_temp_connection()
        self.setCursor(Qt.CrossCursor)

    def exit_transition_creation_mode(self):
        """Exit transition creation mode and clean up."""
        self.transition_creation_mode = False
        self.waiting_for_source = False
        self.waiting_for_target = False
        self.source_node = None
        self._clear_temp_connection()
        self.setCursor(Qt.ArrowCursor)

    def _handle_port_selection(self, item, event):
        """Handle port clicks during transition creation: outgoing port of the
        source block first, then incoming port of the target block."""
        node = None
        is_output = False

        # Find the block node (or one of its ports) under the cursor,
        # ignoring the temp trace
        for candidate in reversed(self.items(event.position().toPoint())):
            if candidate is self.temp_connection:
                continue
            if not candidate.isEnabled():
                continue
            parent = candidate.parentItem()
            if isinstance(candidate, QGraphicsEllipseItem) and isinstance(parent, BlockNode):
                node = parent
                is_output = (candidate is parent.output_port)
                break
            if isinstance(candidate, BlockNode):
                mouse_scene_pos = self.mapToScene(event.position().toPoint())
                # TSK14: an edge without a visible port (Start left, End right) counts as off-port
                if candidate.has_output_port() and (mouse_scene_pos - candidate.get_right_port_position()).manhattanLength() < _PORT_CLICK_THRESHOLD:
                    node = candidate
                    is_output = True
                    break
                if candidate.has_input_port() and (mouse_scene_pos - candidate.get_left_port_position()).manhattanLength() < _PORT_CLICK_THRESHOLD:
                    node = candidate
                    is_output = False
                    break
                break  # clicked on the node body, not near a port

        if node is None:
            if self.info_bar:
                self.info_bar.show_message("Transition creation cancelled")
            self.exit_transition_creation_mode()
            return

        if self.waiting_for_source:
            if not is_output:
                if self.info_bar:
                    self.info_bar.show_message("Start from the outgoing port (right) of the source block")
                self.exit_transition_creation_mode()
                return
            self.source_node = node
            self.waiting_for_source = False
            self.waiting_for_target = True
            mouse_scene_pos = self.mapToScene(event.position().toPoint())
            self._create_temp_connection(node.get_right_port_position(), mouse_scene_pos)
        elif self.waiting_for_target:
            if is_output:
                if self.info_bar:
                    self.info_bar.show_message("End on the incoming port (left) of the target block")
                self.exit_transition_creation_mode()
                return
            target_node = node
            source_node = self.source_node
            self.exit_transition_creation_mode()
            # The model is written by the MainWindow use case (RG058), which
            # validates the block-type matrix (RG028) and the duplicate pair
            self.transition_created.emit(source_node, target_node)

    def _create_temp_connection(self, start_pos: QPointF, end_pos: QPointF):
        """Create the temporary trace for the rubber-band effect."""
        self._clear_temp_connection()
        path = QPainterPath()
        path.moveTo(start_pos)
        path.lineTo(end_pos)
        pen = QPen(QColor(_TEMP_CONNECTION_COLOR), 2, Qt.DashLine)
        pen.setDashPattern(Connection.DASH_PATTERN)
        self.temp_connection = self.scene.addPath(path, pen)
        self.temp_connection.setZValue(100)

    def _update_temp_connection(self, end_pos: QPointF):
        """Update the temporary trace to follow the cursor."""
        if self.temp_connection and self.source_node:
            start_pos = self.source_node.get_right_port_position()
            path = QPainterPath()
            path.moveTo(start_pos)
            path.lineTo(end_pos)
            self.temp_connection.setPath(path)

    def _clear_temp_connection(self):
        """Remove the temporary trace if it exists."""
        if self.temp_connection:
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None

    # ------------------------------------------------------------------
    # Scene population (blocks, transitions, badges)
    # ------------------------------------------------------------------

    def create_block_node(self, block: Block, layout, select: bool = True,
                          skip_overlap_check: bool = False):
        """Create a BlockNode from the business block and its layout.

        RG050: unless skip_overlap_check (loading saved positions), the
        position is adjusted to avoid overlapping an existing block.
        """
        node = BlockNode(block, layout)

        if not skip_overlap_check:
            existing_rects = []
            for item in self.scene.items():
                if isinstance(item, BlockNode):
                    r = item.rect()
                    pos = item.pos()
                    existing_rects.append((pos.x(), pos.y(), r.width(), r.height()))
            layout.x, layout.y = LayoutService.find_non_overlapping_position(
                layout.x, layout.y, layout.width, layout.height, existing_rects
            )

        self.add_item_at(layout.x, layout.y, node)
        # moving this block re-routes the transitions it is not part of (RG052)
        node.register_position_observer(lambda n=node: self._on_node_moved(n))
        if select:
            self._select_item_only(node)

        self.refresh_participation_badge(node)
        self.apply_journey_filter()
        return node

    def refresh_participation_badge(self, block_node: BlockNode) -> None:
        """Refresh the participation badge of a block from the model (FN030)."""
        if not self.narrative_map:
            return
        project = getattr(getattr(self.main_window, 'project_service', None), 'current_project', None)
        agent_lb = {a.id: a.lb for a in project.agent} if project else {}
        labels = [agent_lb[p.agent_id] for p in self.narrative_map.participation
                  if p.block_id == block_node.entity.id and p.agent_id in agent_lb]
        block_node.refresh_participation_badge(len(labels), labels)

    def refresh_all_participation_badges(self) -> None:
        """Refresh the participation badge of every block node."""
        for item in self.scene.items():
            if isinstance(item, BlockNode):
                self.refresh_participation_badge(item)

    def create_connection_from_data(self, source_node: BlockNode, target_node: BlockNode,
                                    transition: Transition, select: bool = False):
        """Create a Connection visual item for a Transition entity."""
        connection_layout = LayoutService.create_connection_layout(
            source_node.entity.id, target_node.entity.id, relation_id=transition.id
        )
        connection = Connection(connection_layout, source_node, target_node, transition)
        self.scene.addItem(connection)
        connection.update_path()
        if select:
            self._select_item_only(connection)
        self.apply_journey_filter()
        return connection

    def find_block_node(self, block_id: int):
        """Find the BlockNode of a business block id."""
        for item in self.scene.items():
            if isinstance(item, BlockNode) and item.entity.id == block_id:
                return item
        return None

    def find_connection(self, transition_id: int):
        """Find the Connection of a business transition id."""
        for item in self.scene.items():
            if isinstance(item, Connection) and item.get_relation_id() == transition_id:
                return item
        return None

    def has_connection_between(self, source_node, target_node) -> bool:
        """True when a visual transition already links the two nodes."""
        for item in self.scene.items():
            if isinstance(item, Connection):
                if item.source_node is source_node and item.target_node is target_node:
                    return True
        return False

    def next_free_position(self, x: float = 2000.0, y: float = 2000.0):
        """First grid-snapped, non-overlapping position near (x, y) (RG050)."""
        existing_rects = []
        for item in self.scene.items():
            if isinstance(item, BlockNode):
                r = item.rect()
                pos = item.pos()
                existing_rects.append((pos.x(), pos.y(), r.width(), r.height()))
        w = _get_config("node_default_width", 80.0)
        h = _get_config("node_default_height", 40.0)
        x, y = LayoutService.find_non_overlapping_position(x, y, w, h, existing_rects)
        return LayoutService.snap_to_grid(x), LayoutService.snap_to_grid(y)

    def _on_node_moved(self, moved_node):
        """Re-route the transitions not endpoint of the moved block (RG052)
        and notify the MainWindow (FN017: a move marks the project modified)."""
        for item in self.scene.items():
            if not isinstance(item, Connection):
                continue
            if item.source_node is moved_node or item.target_node is moved_node:
                continue
            item.update_path()
        self.workspace_modified.emit()

    def _select_item_only(self, item):
        """Select only the given item, deselect the others (RG049)."""
        for existing_item in self.scene.items():
            if (existing_item is not item
                    and existing_item.flags() & QGraphicsItem.ItemIsSelectable
                    and existing_item.isEnabled()):
                existing_item.setSelected(False)
        if item.flags() & QGraphicsItem.ItemIsSelectable:
            item.setSelected(True)

    def _clear_all_selections(self):
        """Deselect every selectable item (RG049: a click on empty space)."""
        for item in self.scene.items():
            if (item.flags() & QGraphicsItem.ItemIsSelectable and item.isEnabled()):
                item.setSelected(False)

    def get_selected_item(self):
        """Return the single selected item (BlockNode or Connection), or None."""
        selected = [i for i in self.scene.selectedItems()
                    if isinstance(i, (BlockNode, Connection))]
        return selected[0] if selected else None

    def remove_connection(self, connection: Connection) -> bool:
        """Remove a transition visual item from the scene."""
        if connection is None:
            return False
        self.scene.removeItem(connection)
        self.apply_journey_filter()
        return True

    def remove_node(self, node: BlockNode) -> bool:
        """Remove a block node and its attached transitions from the scene."""
        if node is None:
            return False
        connections_to_remove = [
            item for item in self.scene.items()
            if isinstance(item, Connection)
            and (item.source_node is node or item.target_node is node)
        ]
        for connection in connections_to_remove:
            self.scene.removeItem(connection)
        self.scene.removeItem(node)
        self.apply_journey_filter()
        return True

    # ------------------------------------------------------------------
    # Visual layout persistence (RG060)
    # ------------------------------------------------------------------

    def collect_workspace_layout(self) -> WorkspaceLayout:
        """Collect the current visual layout for persistence (RG060)."""
        layout = WorkspaceLayout(narrative_map_id=self.narrative_map.id)
        for item in self.scene.items():
            if isinstance(item, Connection):
                layout.add_connection(item.layout)
            elif isinstance(item, BlockNode):
                layout.add_node(item.layout)
        layout.zoom_level = self.transform().m11()
        layout.scroll_x = float(self.horizontalScrollBar().value())
        layout.scroll_y = float(self.verticalScrollBar().value())
        return layout

    def populate_from_layout(self, workspace_layout: WorkspaceLayout, narrative_map) -> int:
        """Rebuild the visual blocks and transitions from a saved layout."""
        node_count = 0
        for node_id in sorted(workspace_layout.block_nodes.keys()):
            node_layout = workspace_layout.block_nodes[node_id]
            entity = next((b for b in narrative_map.block if b.id == node_layout.node_id), None)
            if entity is None:
                logger.warning("Block entity not found for node_id=%s", node_layout.node_id)
                continue
            self.create_block_node(entity, node_layout, select=False, skip_overlap_check=True)
            node_count += 1

        for relation_id in sorted(workspace_layout.transition_connections.keys()):
            conn_layout = workspace_layout.transition_connections[relation_id]
            source_node = self.find_block_node(conn_layout.source_node_id)
            target_node = self.find_block_node(conn_layout.target_node_id)
            transition = next((t for t in narrative_map.transition if t.id == conn_layout.relation_id), None)
            if not (source_node and target_node and transition):
                logger.warning("Transition %s: source/target/transition not found", relation_id)
                continue
            self.create_connection_from_data(source_node, target_node, transition)

        if workspace_layout.zoom_level != 1.0:
            self.resetTransform()
            self.scale(workspace_layout.zoom_level, workspace_layout.zoom_level)
        self.horizontalScrollBar().setValue(int(workspace_layout.scroll_x))
        self.verticalScrollBar().setValue(int(workspace_layout.scroll_y))

        self.refresh_all_participation_badges()
        self._clear_all_selections()
        self.apply_journey_filter()
        return node_count

    def populate_default(self, narrative_map) -> int:
        """Create the visual items with default positions (no saved layout):
        blocks in a column around the center of the scene."""
        node_count = 0
        start_x = 1800.0
        start_y = 1800.0
        step_y = 120.0
        for i, block in enumerate(narrative_map.block):
            layout = LayoutService.create_node_layout(
                node_id=block.id, node_type=block.typ, x=start_x, y=start_y + i * step_y
            )
            self.create_block_node(block, layout, select=False, skip_overlap_check=True)
            node_count += 1

        for transition in narrative_map.transition:
            source_node = self.find_block_node(transition.from_block_id)
            target_node = self.find_block_node(transition.to_block_id)
            if source_node and target_node:
                self.create_connection_from_data(source_node, target_node, transition)

        self.refresh_all_participation_badges()
        self._clear_all_selections()
        self.apply_journey_filter()
        return node_count

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
        # RG048: an item outside the journey filter behaves as empty area
        if item is not None and not item.isEnabled():
            item = None
        # Climb to the parent block node when a child (port, label, badge) is hit
        if item is not None and not isinstance(item, (BlockNode, Connection)):
            parent = item.parentItem()
            item = parent if isinstance(parent, BlockNode) else None

        if isinstance(item, (BlockNode, Connection)):
            self._select_item_only(item)
        else:
            self._clear_all_selections()

        self.context_menu_requested.emit(item, self.mapToGlobal(pos))
