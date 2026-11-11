# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : base_node.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Base Node for Hyperscript.

This module provides the base class for all visual nodes displayed in the
Journeys workspace. It inherits from QGraphicsRectItem and adds functionality
for:
- Storing a reference to the business entity (Block) and its visual layout
- Managing node appearance and behavior
- Handling selection and movement
- Supporting connection ports (incoming left, outgoing right)

The concrete node type is BlockNode.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QGraphicsEllipseItem, QToolTip
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath
from typing import Optional, Any

from core.models.view_model import NodeLayout
from core.services.layout_service import LayoutService
from config.config_loader import get as _get_config
from ui.utils import theme


class BaseNode(QGraphicsRectItem):
    """
    Base class for all visual nodes in the workspace.
    
    This class combines a QGraphicsRectItem with business entity data and
    visual layout information. It serves as the foundation for all node types
    (State, Event, etc.).
    
    Attributes:
        entity: The business entity this node represents (Block)
        layout: The NodeLayout containing visual properties (position, size, etc.)
        label: QGraphicsTextItem for displaying the block's type
        ports: Dictionary of connection ports (for future use)
    """
    
    # Default dimensions (sourced from config.json)
    DEFAULT_WIDTH = _get_config("node_default_width", 80.0)
    DEFAULT_HEIGHT = _get_config("node_default_height", 40.0)

    # Corner radius of the node rectangle (charter 98: ~6px)
    CORNER_RADIUS = _get_config("node_corner_radius_px", 6.0)

    # Default colors (dark theme, charter 98, via ui.utils.theme)
    DEFAULT_BG_COLOR = theme.color("bg_surface", theme.BG_SURFACE)
    DEFAULT_BORDER_COLOR = theme.color("border_color", theme.BORDER_COLOR)
    DEFAULT_TEXT_COLOR = theme.color("text_primary", theme.TEXT_PRIMARY)

    # Hover color: soft white continuous outline (charter 98)
    HOVER_BORDER_COLOR = theme.color("hover_color", theme.HOVER_COLOR)

    # Font settings (charter 98: Segoe UI; entity label ~12px non bold,
    # aligned with the agents matrix — TSK12 point 04)
    _FONT_FAMILY = theme.FONT_FAMILY
    DEFAULT_FONT = QFont(_FONT_FAMILY, theme.NODE_LABEL_FONT_SIZE_PX)
    
    # Port settings (sourced from config.json, Journeys view)
    PORT_SIZE = _get_config("journeys_view_port_size_px", 8)
    PORT_MARGIN = _get_config("journeys_view_port_margin_px", 4)
    
    def __init__(self, entity: Any, layout: NodeLayout):
        """
        Initialize a base node with a business entity and its layout.
        
        Args:
            entity: The business entity (State, Event, etc.)
            layout: The NodeLayout containing visual properties
        """
        # Initialize QGraphicsRectItem with position and size from layout
        width = layout.width if layout.width > 0 else self.DEFAULT_WIDTH
        height = layout.height if layout.height > 0 else self.DEFAULT_HEIGHT
        super().__init__(0, 0, width, height)
        
        # Store references to business and visual models
        self.entity = entity
        self.layout = layout
        
        # Set initial position from layout
        self.setPos(layout.x, layout.y)
        
        # Enable movement and selection
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        
        # Set acceptance for hover events (useful for visual feedback)
        self.setAcceptHoverEvents(True)

        # Hover state (charter 98: hover outline, selection has priority)
        self._hovered = False

        # Initialize appearance
        self._init_appearance()
        
        # Create and add label
        self.label = QGraphicsTextItem(self)
        self._init_label()
        self._position_label()
        
        # Initialize ports (empty dict, to be populated by subclasses if needed)
        self.ports = {}

        # Position change observers (connections that need to update when this node moves)
        self._position_observers = []
        
        # Initialize visual input and output ports
        self.input_port = None  # QGraphicsEllipseItem for input port (left)
        self.output_port = None  # QGraphicsEllipseItem for output port (right)
        self._init_ports()
        
        # Update visual state based on layout
        self.update_from_layout()


    def _init_appearance(self) -> None:
        """Initialize the visual appearance of the node."""
        # Set default pen and brush
        self.setPen(QPen(self.DEFAULT_BORDER_COLOR, 2))
        self.setBrush(QBrush(self.DEFAULT_BG_COLOR))

        # Rounded corners (charter 98: ~6px, no drop shadow)
        self._rounded_rect = None  # built lazily in paint/boundingRect


    def _init_label(self) -> None:
        """Initialize the label with the block's type (session 03: the label
        lb is shown in the hover tooltip only, no truncation needed)."""
        label_text = getattr(self.entity, 'typ', '?')
        self.label.setPlainText(str(label_text))
        
        # Set label font and color
        self.label.setFont(self.DEFAULT_FONT)
        self.label.setDefaultTextColor(self.DEFAULT_TEXT_COLOR)
        
        # Make label non-selectable (selection is handled at node level)
        self.label.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def _position_label(self) -> None:
        """Center the entity label inside the node."""
        if self.label is None:
            return
        text_rect = self.label.boundingRect()
        self.label.setPos(
            (self.rect().width() - text_rect.width()) / 2,
            (self.rect().height() - text_rect.height()) / 2)


    def update_entity_data(self) -> None:
        """
        Refresh the visual representation after the entity data was updated.

        The node displays the block type; the tooltip shows the label (lb)
        and the note (session 03 decision, RG054).
        """
        typ = getattr(self.entity, 'typ', None)
        if typ is not None:
            self.label.setPlainText(str(typ))
            self._position_label()
        lb = getattr(self.entity, 'lb', None)
        note = getattr(self.entity, 'note', None)
        tooltip = str(lb) if lb else ''
        if note:
            tooltip += f"\n{note}" if tooltip else str(note)
        self.setToolTip(tooltip)

    def _init_ports(self) -> None:
        """
        Initialize visual input and output ports as ellipse items.
        
        Creates two ports:
        - Input port (left side, red) for incoming connections
        - Output port (right side, green) for outgoing connections
        """
        port_size = self.PORT_SIZE
        
        # Anchor color (charter 98): single soft white for all anchors,
        # dark fill matching the canvas background
        anchor_fill = theme.color("bg_primary", theme.BG_PRIMARY)
        anchor_stroke = theme.color("anchor_color", theme.ANCHOR_COLOR)

        # Input port (left side, centered vertically)
        self.input_port = QGraphicsEllipseItem(
            -port_size / 2,  # x: positioned at left edge
            self.rect().height() / 2 - port_size / 2,  # y: centered vertically
            port_size, port_size,
            self
        )
        self.input_port.setBrush(QBrush(anchor_fill))
        self.input_port.setPen(QPen(anchor_stroke, 1.5))
        self.input_port.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.input_port.setFlag(QGraphicsItem.ItemIsMovable, False)

        # Output port (right side, centered vertically)
        self.output_port = QGraphicsEllipseItem(
            self.rect().width() - port_size / 2,  # x: positioned at right edge
            self.rect().height() / 2 - port_size / 2,  # y: centered vertically
            port_size, port_size,
            self
        )
        self.output_port.setBrush(QBrush(anchor_fill))
        self.output_port.setPen(QPen(anchor_stroke, 1.5))
        self.output_port.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.output_port.setFlag(QGraphicsItem.ItemIsMovable, False)

    def update_from_layout(self) -> None:
        """
        Update the node's visual properties from its layout.
        
        This method should be called when the layout is modified externally
        or when loading a node from disk.
        """
        # Update position
        self.setPos(self.layout.x, self.layout.y)
        
        # Update size
        if self.layout.width > 0 and self.layout.height > 0:
            self.setRect(0, 0, self.layout.width, self.layout.height)
        
        # Update selection state (ItemSelectedChange reapplies the
        # outline: dashed type color when selected, charter 98)
        self.setSelected(self.layout.selected)
        if not self.layout.selected:
            self._apply_outline()

        # Update color if specified (layout color overrides the surface;
        # the type outline is preserved, charter 98)
        if self.layout.color:
            try:
                color = QColor(self.layout.color)
                if color.isValid():
                    self.setBrush(QBrush(color))
            except (ValueError, AttributeError):
                pass

        # Update port positions when node size changes
        self._update_port_positions()
        self._position_label()


    def update_layout(self) -> None:
        """
        Update the layout object with the node's current properties.
        
        This should be called when the node is moved or resized to
        persist the changes to the layout model.
        """
        # Update position
        self.layout.x = self.x()
        self.layout.y = self.y()
        
        # Update size
        self.layout.width = self.rect().width()
        self.layout.height = self.rect().height()
        
        # Update selection state
        self.layout.selected = self.isSelected()


    def _type_border_color(self) -> QColor:
        """Return the border color of the node's type (charter 98).

        BaseNode has no type: the neutral border color applies. TypedNode
        subclasses override this with their type color (gold/copper).
        """
        return self.DEFAULT_BORDER_COLOR

    def _apply_outline(self, selected: Optional[bool] = None) -> None:
        """Apply the outline according to the priority rule (charter 98):
        selection (dashed, type color) > hover (soft white, solid) > type.

        A custom dash pattern is only honored by Qt for DashLine pens:
        Qt.DotLine renders a fixed dot pattern, so DashLine with a 6/4
        pattern is used to match the charter's dotted selection outline.

        Args:
            selected: Explicit selection state. During
                itemChange(ItemSelectedChange), isSelected() still holds
                the previous state, so the new value must be passed.
        """
        if selected if selected is not None else self.isSelected():
            pen = QPen(self._type_border_color(), 2)
            pen.setStyle(Qt.DashLine)
            pen.setDashPattern([6.0, 4.0])
            pen.setCapStyle(Qt.FlatCap)
            self.setPen(pen)
        elif self._hovered:
            self.setPen(QPen(self.HOVER_BORDER_COLOR, 2))
        else:
            self.setPen(QPen(self._type_border_color(), 2))

    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the node's appearance based on selection state.

        Charter 98: selection is shown by a dashed outline in the node's
        type color (no dedicated selection color); the background stays
        the surface color.

        Args:
            selected: Whether the node is selected
        """
        self._apply_outline(selected)


    # -------------------------------------------------------------------------
    # QGraphicsItem overrides
    # -------------------------------------------------------------------------

    def _rounded_path(self) -> QPainterPath:
        """Return the node rectangle as a rounded-corner path (charter 98)."""
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.CORNER_RADIUS, self.CORNER_RADIUS)
        return path

    def boundingRect(self):
        """Bounding rect covering the rounded outline (pen width included)."""
        return self._rounded_path().boundingRect().adjusted(-2, -2, 2, 2)

    def shape(self):
        """Clickable shape: the rounded rectangle (hit-testing, AGENTS.md)."""
        return self._rounded_path()

    def paint(self, painter, option, widget=None) -> None:
        """Paint the node as a rounded rectangle (charter 98: radius ~6px,
        no drop shadow)."""
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPath(self._rounded_path())

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events."""
        # Call parent implementation first
        super().mousePressEvent(event)
        
        # Update selection appearance
        self.set_selected_appearance(self.isSelected())


    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release events."""
        super().mouseReleaseEvent(event)
        
        # Update layout after movement
        if self.isSelected():
            self.update_layout()


    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move events (during drag)."""
        super().mouseMoveEvent(event)
        
        # Update layout during movement
        if event.buttons() == Qt.LeftButton:
            self.update_layout()


    def hoverEnterEvent(self, event) -> None:
        """Handle hover enter events."""
        # Visual feedback for hover: soft white outline (charter 98).
        # Selection has priority: a selected node keeps its dashed
        # type-colored outline even when hovered.
        self._hovered = True
        self._apply_outline()
        # Tooltip: label + note IMMEDIATELY, bypassing the system hover
        # delay (~1s). The workspace swallows Qt's delayed automatic
        # tooltip event (see JourneysWorkspace.viewportEvent), which would
        # otherwise pop a second tooltip at the cursor when the mouse rests.
        tooltip = self.toolTip()
        if tooltip:
            QToolTip.showText(event.screenPos(), tooltip)
        super().hoverEnterEvent(event)


    def hoverLeaveEvent(self, event) -> None:
        """Handle hover leave events."""
        # Restore normal appearance (selection keeps its dashed outline)
        self._hovered = False
        self._apply_outline()
        # Hide the tooltip shown on hover
        QToolTip.hideText()
        super().hoverLeaveEvent(event)


    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """
        Handle item changes (e.g., selection, position).
        
        This is called automatically by Qt when certain properties change.
        """
        if change == QGraphicsItem.ItemSelectedChange:
            self.set_selected_appearance(bool(value))
            self.layout.selected = bool(value)
        elif change == QGraphicsItem.ItemPositionChange:
            # Constrains the movement to the limits of the scene (absolute limit)
            new_pos = value
            scene = self.scene()
            if scene:
                scene_rect = scene.sceneRect()
                # Use self.rect() for dimensions (independent of position)
                node_width = self.rect().width()
                node_height = self.rect().height()
                
                # Constraints to keep the node ENTIRELY within the scene
                max_x = scene_rect.right() - node_width
                max_y = scene_rect.bottom() - node_height
                min_x = scene_rect.left()
                min_y = scene_rect.top()
                
                constrained_x = max(min_x, min(new_pos.x(), max_x))
                constrained_y = max(min_y, min(new_pos.y(), max_y))

                # RG046: snap to grid after scene constraints
                constrained_x = LayoutService.snap_to_grid(constrained_x)
                constrained_y = LayoutService.snap_to_grid(constrained_y)

                # Update the layout with the constrained position.
                self.layout.x = constrained_x
                self.layout.y = constrained_y

                result = QPointF(constrained_x, constrained_y)
                self._notify_position_observers()
                return result

        return super().itemChange(change, value)

    def register_position_observer(self, callback) -> None:
        """Register a callback to be called when this node's position changes."""
        if callback not in self._position_observers:
            self._position_observers.append(callback)

    def unregister_position_observer(self, callback) -> None:
        """Remove a previously registered position observer."""
        if callback in self._position_observers:
            self._position_observers.remove(callback)

    def _notify_position_observers(self) -> None:
        """Notify all registered position observers."""
        for callback in self._position_observers:
            callback()


    # -------------------------------------------------------------------------
    # Connection port methods (for future use)
    # -------------------------------------------------------------------------
    
    def get_port_position(self, port_name: str) -> QPointF:
        """
        Get the scene position of a connection port.
        
        This method should be overridden by subclasses to provide
        specific port positions based on their layout.
        
        Args:
            port_name: Name of the port (e.g., 'left', 'right')
            
        Returns:
            Position of the port in scene coordinates
        """
        # Default implementation: return center of the node
        return self.sceneBoundingRect().center()


    def _update_port_positions(self) -> None:
        """
        Update the positions of input and output ports based on current node size.

        This should be called whenever the node is resized.
        """
        if self.input_port and self.output_port:
            port_size = self.PORT_SIZE
            node_height = self.rect().height()

            # Position input port (left side)
            self.input_port.setRect(
                -port_size / 2,
                node_height / 2 - port_size / 2,
                port_size, port_size
            )

            # Position output port (right side)
            self.output_port.setRect(
                self.rect().width() - port_size / 2,
                node_height / 2 - port_size / 2,
                port_size, port_size
            )

    def get_left_port_position(self) -> QPointF:
        """Get the position of the left connection port (input port)."""
        if self.input_port:
            return self.input_port.sceneBoundingRect().center()
        rect = self.sceneBoundingRect()
        return QPointF(rect.left(), rect.center().y())


    def get_right_port_position(self) -> QPointF:
        """Get the position of the right connection port (output port)."""
        if self.output_port:
            return self.output_port.sceneBoundingRect().center()
        rect = self.sceneBoundingRect()
        return QPointF(rect.right(), rect.center().y())

    def has_input_port(self) -> bool:
        """TSK14: the incoming (left) port is visible (hidden for Start blocks)."""
        return self.input_port is not None and self.input_port.isVisible()

    def has_output_port(self) -> bool:
        """TSK14: the outgoing (right) port is visible (hidden for End blocks)."""
        return self.output_port is not None and self.output_port.isVisible()


    def add_port(self, name: str, position: QPointF) -> None:
        """
        Add a connection port to the node.
        
        Args:
            name: Name of the port
            position: Position relative to the node (0-1 in both axes)
        """
        self.ports[name] = position

    def get_port(self, name: str) -> Optional[QPointF]:
        """
        Get the position of a port by name.
        
        Args:
            name: Name of the port
            
        Returns:
            Position of the port in node coordinates, or None if not found
        """
        return self.ports.get(name)


    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    
    def center(self) -> QPointF:
        """Get the center position of the node in scene coordinates."""
        return self.sceneBoundingRect().center()


class TypedNode(BaseNode):
    """
    Base class for typed block nodes.

    The border color is the block type color (config.json block_*_color,
    adopted session 03); the background is the shared surface color,
    selection is a dashed outline in the type color, and anchors share a
    single soft white. The entity is stored as self.entity (set by BaseNode).
    """

    def __init__(self, entity, layout):
        super().__init__(entity, layout)

    def _type_border_color(self) -> QColor:
        """Border color of the block's type (block_*_color in config.json)."""
        return QColor(theme.block_color(getattr(self.entity, 'typ', 'Scene')))

    def _update_colors(self) -> None:
        """Update node colors: shared surface background, type-colored outline."""
        self.setBrush(QBrush(theme.color("bg_surface", theme.BG_SURFACE)))
        self._apply_outline()
        if self.label:
            self.label.setDefaultTextColor(theme.color("text_primary", theme.TEXT_PRIMARY))

    def update_from_layout(self) -> None:
        """Update visual properties from layout, re-applying type colors."""
        super().update_from_layout()
        self._update_colors()

    def set_note(self, note: str) -> None:
        """Set the entity's note."""
        self.entity.note = note

    def get_note(self) -> Optional[str]:
        """Get the entity's note."""
        return self.entity.note

    def get_port_position(self, port_name: str) -> QPointF:
        """Get the scene position of a connection port ('left' or 'right')."""
        port_name = port_name.lower()
        if port_name == "left":
            return self.get_left_port_position()
        elif port_name == "right":
            return self.get_right_port_position()
