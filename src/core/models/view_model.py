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
dedicated file per narrative map, separate from the business model. Agent
card positions belong to the project (RG057) and are stored in a
project-level file (RG067).
Node dimensions are sourced from config.json (single source of truth).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List

from config.config_loader import get as _get_config

# Node dimensions sourced from config.json (single source of truth).
_NODE_DEFAULT_WIDTH = _get_config("node_default_width", 80.0)
_NODE_DEFAULT_HEIGHT = _get_config("node_default_height", 40.0)

# Agent card dimensions sourced from config.json (Agents view, RG066).
_AGENT_CARD_DEFAULT_WIDTH = _get_config("agents_view_card_width", 160.0)
_AGENT_CARD_DEFAULT_HEIGHT = _get_config("agents_view_card_height", 100.0)


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
    """
    narrative_map_id: str
    block_nodes: Dict[int, NodeLayout] = field(default_factory=dict)
    transition_connections: Dict[int, ConnectionLayout] = field(default_factory=dict)
    zoom_level: float = 1.0
    scroll_x: float = 0.0
    scroll_y: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'narrative_map_id': self.narrative_map_id,
            'block_nodes': {k: v.to_dict() for k, v in self.block_nodes.items()},
            'transition_connections': {k: v.to_dict() for k, v in self.transition_connections.items()},
            'zoom_level': self.zoom_level,
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y,
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
        )


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


@dataclass
class AgentCardLayout:
    """
    Visual layout of a single agent card in the "Agents" view (RG066/RG067).

    Attributes:
        agent_id: The ID of the business entity (Agent.id)
        x: X position in pixels (workspace coordinates, origin of an invisible cell)
        y: Y position in pixels (workspace coordinates, origin of an invisible cell)
        width: Width of the card in pixels (agents_view_card_width)
        height: Height of the card in pixels (agents_view_card_height)
        selected: Whether the card is currently selected
    """
    agent_id: int
    x: float
    y: float
    width: float = _AGENT_CARD_DEFAULT_WIDTH
    height: float = _AGENT_CARD_DEFAULT_HEIGHT
    selected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'agent_id': self.agent_id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'selected': self.selected
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCardLayout':
        """Create an AgentCardLayout from a dictionary."""
        return cls(
            agent_id=int(data['agent_id']),
            x=float(data['x']),
            y=float(data['y']),
            width=float(data.get('width', _AGENT_CARD_DEFAULT_WIDTH)),
            height=float(data.get('height', _AGENT_CARD_DEFAULT_HEIGHT)),
            selected=bool(data.get('selected', False))
        )


@dataclass
class ProjectLayout:
    """
    Project-level visual layout (RG067).

    Agents belong to the project (RG057), not to a narrative map, so the
    positions of their cards in the "Agents" view are stored in a dedicated
    project-level file (layouts/project.json), separate from the per-map
    workspace layouts. Purely visual data: no business value.

    Attributes:
        agent_cards: Dict keyed by Agent.id
        relationships_view_agent_order: shared order of the rows AND columns of
            the "Relationships" matrix (Agent ids, RG070 revised session 10
            TSK32 - upper-triangle matrix, a single order for both axes)
    """
    agent_cards: Dict[int, AgentCardLayout] = field(default_factory=dict)
    relationships_view_agent_order: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'agent_cards': {str(k): v.to_dict() for k, v in self.agent_cards.items()},
            'relationships_view_agent_order': [int(a) for a in self.relationships_view_agent_order],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectLayout':
        """Create a ProjectLayout from a dictionary. Migrations: TSK27 -> TSK29
        (single `relationships_axis_order`) then TSK29 -> TSK32 (independent
        `row_order`/`column_order` -> shared `agent_order`, the row order wins)."""
        legacy_axis = [int(a) for a in data.get('relationships_axis_order', [])]
        legacy_row = [int(a) for a in data.get('relationships_view_row_order', legacy_axis)]
        agent_order = [int(a) for a in data.get(
            'relationships_view_agent_order', legacy_row)]
        return cls(
            agent_cards={int(k): AgentCardLayout.from_dict(v)
                         for k, v in data.get('agent_cards', {}).items()},
            relationships_view_agent_order=agent_order,
        )

    def get_agent_card_layout(self, agent_id: int) -> Optional[AgentCardLayout]:
        """Get the layout of an agent card by Agent.id."""
        return self.agent_cards.get(agent_id)

    def add_agent_card(self, card_layout: AgentCardLayout) -> None:
        """Add or update an agent card layout."""
        self.agent_cards[card_layout.agent_id] = card_layout

    def remove_agent_card(self, agent_id: int) -> bool:
        """Remove an agent card layout by Agent.id."""
        if agent_id in self.agent_cards:
            del self.agent_cards[agent_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all agent card layouts."""
        self.agent_cards.clear()
