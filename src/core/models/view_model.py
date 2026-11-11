# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : view_model.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
View model of Hyperscript: visual layout of the workspaces (RG060).

Purely visual data (positions, sizes, styles, zoom, scroll), stored in a
dedicated file per narrative map, separate from the business model.
Node dimensions are sourced from config.json (single source of truth).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List

from config.config_loader import get as _get_config

# Node dimensions sourced from config.json (single source of truth).
_NODE_DEFAULT_WIDTH = _get_config("node_default_width", 80.0)
_NODE_DEFAULT_HEIGHT = _get_config("node_default_height", 40.0)


class BlockType(Enum):
    """Visual type of a node: one narrative block type (matches Block.typ)."""
    START = "Start"
    SCENE = "Scene"
    PIVOT = "Pivot"
    CONDITION = "Condition"
    END = "End"


@dataclass
class NodeLayout:
    """
    Visual layout of a single node (narrative block) in the workspace.

    Attributes:
        node_id: The ID of the business entity (Block.id)
        node_type: The block type (used for deserialization)
        x: X position in pixels (workspace coordinates)
        y: Y position in pixels (workspace coordinates)
        width: Width of the node in pixels
        height: Height of the node in pixels
        color: Optional hex color code (#RRGGBB) for custom styling
        z_index: Z-order for layering (higher values appear on top)
        collapsed: Whether the node is collapsed (hidden content)
        selected: Whether the node is currently selected
    """
    node_id: int
    node_type: BlockType
    x: float
    y: float
    width: float = _NODE_DEFAULT_WIDTH
    height: float = _NODE_DEFAULT_HEIGHT
    color: Optional[str] = None
    z_index: int = 0
    collapsed: bool = False
    selected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'node_id': self.node_id,
            'node_type': self.node_type.value,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'color': self.color,
            'z_index': self.z_index,
            'collapsed': self.collapsed,
            'selected': self.selected
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeLayout':
        """Create a NodeLayout from a dictionary."""
        return cls(
            node_id=int(data['node_id']),
            node_type=BlockType(data['node_type']),
            x=float(data['x']),
            y=float(data['y']),
            width=float(data.get('width', _NODE_DEFAULT_WIDTH)),
            height=float(data.get('height', _NODE_DEFAULT_HEIGHT)),
            color=data.get('color'),
            z_index=int(data.get('z_index', 0)),
            collapsed=bool(data.get('collapsed', False)),
            selected=bool(data.get('selected', False))
        )


class ConnectionStyle(Enum):
    """Enumeration of connection line styles."""
    STRAIGHT = "straight"      # Direct line between nodes
    CURVED = "curved"          # Bezier curve connection
    DOTTED = "dotted"          # Dotted line
    DASHED = "dashed"          # Dashed line
    ARROW = "arrow"            # Straight line with arrowhead
    CURVED_ARROW = "curved_arrow"  # Curved line with arrowhead


class PortPosition(Enum):
    """Enumeration of connection port positions on a node."""
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"


@dataclass
class ConnectionLayout:
    """
    Visual layout of a connection (transition) between two blocks.

    The connection is identified by its relation_id (the Transition.id),
    used as the key in the WorkspaceLayout connections dictionary.

    Attributes:
        source_node_id: ID of the source block
        source_port: Connection port on the source node
        target_node_id: ID of the target block
        target_port: Connection port on the target node
        style: Visual style of the connection line
        color: Optional hex color code (#RRGGBB)
        thickness: Line thickness in pixels
        z_index: Z-order for layering
        selected: Whether the connection is currently selected
        label: Optional text label for the connection
        relation_id: ID of the transition (Transition.id)
        relation_type: Type of the business relation ("Transition")
    """
    source_node_id: int = -1
    source_port: PortPosition = PortPosition.RIGHT
    target_node_id: int = -1
    target_port: PortPosition = PortPosition.LEFT
    style: ConnectionStyle = ConnectionStyle.ARROW
    color: Optional[str] = None
    thickness: float = 2.0
    z_index: int = 0
    selected: bool = False
    label: Optional[str] = None
    relation_id: Optional[int] = None
    relation_type: Optional[str] = "Transition"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'source_node_id': self.source_node_id,
            'source_port': self.source_port.value,
            'target_node_id': self.target_node_id,
            'target_port': self.target_port.value,
            'style': self.style.value,
            'color': self.color,
            'thickness': self.thickness,
            'z_index': self.z_index,
            'selected': self.selected,
            'label': self.label,
            'relation_id': self.relation_id,
            'relation_type': self.relation_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConnectionLayout':
        """Create a ConnectionLayout from a dictionary."""
        return cls(
            source_node_id=int(data['source_node_id']),
            source_port=PortPosition(data.get('source_port', 'right')),
            target_node_id=int(data['target_node_id']),
            target_port=PortPosition(data.get('target_port', 'left')),
            style=ConnectionStyle(data.get('style', 'straight')),
            color=data.get('color'),
            thickness=float(data.get('thickness', 2.0)),
            z_index=int(data.get('z_index', 0)),
            selected=bool(data.get('selected', False)),
            label=data.get('label'),
            relation_id=int(data['relation_id']) if data.get('relation_id') is not None else None,
            relation_type=data.get('relation_type', 'Transition')
        )


@dataclass
class WorkspaceLayout:
    """
    Complete visual layout of a workspace (view).

    Attributes:
        narrative_map_id: ID of the associated NarrativeMap from the business model
        block_nodes: Dict keyed by Block.id
        transition_connections: Dict keyed by Transition.id
        zoom_level: Current zoom level of the workspace (1.0 = 100%)
        scroll_x / scroll_y: Current scroll position of the workspace
        agents_view_column_order: Custom order of the agents view matrix
            columns (Block IDs, RG036); empty = creation order
        agents_view_row_order: Custom order of the agents view matrix rows
            (Agent IDs, RG036); empty = creation order
    """
    narrative_map_id: str
    block_nodes: Dict[int, NodeLayout] = field(default_factory=dict)
    transition_connections: Dict[int, ConnectionLayout] = field(default_factory=dict)
    zoom_level: float = 1.0
    scroll_x: float = 0.0
    scroll_y: float = 0.0
    agents_view_column_order: List[int] = field(default_factory=list)
    agents_view_row_order: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'narrative_map_id': self.narrative_map_id,
            'block_nodes': {k: v.to_dict() for k, v in self.block_nodes.items()},
            'transition_connections': {k: v.to_dict() for k, v in self.transition_connections.items()},
            'zoom_level': self.zoom_level,
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y,
            'agents_view_column_order': list(self.agents_view_column_order),
            'agents_view_row_order': list(self.agents_view_row_order)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkspaceLayout':
        """Create a WorkspaceLayout from a dictionary."""
        return cls(
            narrative_map_id=str(data['narrative_map_id']),
            block_nodes={int(k): NodeLayout.from_dict(v) for k, v in data.get('block_nodes', {}).items()},
            transition_connections={int(k): ConnectionLayout.from_dict(v) for k, v in data.get('transition_connections', {}).items()},
            zoom_level=float(data.get('zoom_level', 1.0)),
            scroll_x=float(data.get('scroll_x', 0.0)),
            scroll_y=float(data.get('scroll_y', 0.0)),
            agents_view_column_order=[int(i) for i in data.get('agents_view_column_order', [])],
            agents_view_row_order=[int(i) for i in data.get('agents_view_row_order', [])]
        )

    def get_node_layout(self, node_type: BlockType, node_id: int) -> Optional[NodeLayout]:
        """Get the layout of a block (block types all share the same node dict)."""
        return self.block_nodes.get(node_id)

    def get_connection_layout(self, relation_id: int) -> Optional[ConnectionLayout]:
        """Get the layout of a transition by its ID."""
        return self.transition_connections.get(relation_id)

    def add_node(self, node_layout: NodeLayout) -> None:
        """Add or update a block node layout."""
        self.block_nodes[node_layout.node_id] = node_layout

    def add_connection(self, connection_layout: ConnectionLayout) -> None:
        """Add or update a transition connection layout."""
        self.transition_connections[connection_layout.relation_id] = connection_layout

    def remove_connection(self, relation_id: int) -> bool:
        """Remove a transition connection layout by its ID."""
        if relation_id in self.transition_connections:
            del self.transition_connections[relation_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all nodes and connections from the layout."""
        self.block_nodes.clear()
        self.transition_connections.clear()
        self.zoom_level = 1.0
        self.scroll_x = 0.0
        self.scroll_y = 0.0
        self.agents_view_column_order.clear()
        self.agents_view_row_order.clear()
