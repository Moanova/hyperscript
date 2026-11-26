# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : layout_service.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Layout Service for Hyperscript.

This module provides services for persisting and loading visual layouts
(workspace layouts) to/from the filesystem. It handles the storage of
node positions, connection paths, zoom levels, and scroll positions
separately from the business data model.

Layout files are stored in a subdirectory named after the project file:
    {project_file_dir}/{project_file_stem}/layouts/{narrative_map_id}.json
plus the project-level layout (agent card positions, RG067):
    {project_file_dir}/{project_file_stem}/layouts/project.json

Example:
    /user/projects/my_project.json
    /user/projects/my_project/layouts/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv.json
    /user/projects/my_project/layouts/project.json

This ensures that:
- All files related to a project are grouped together
- Users can easily identify which layout folder belongs to which project
- Moving the project file and its folder together preserves all data
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

from core.models.view_model import (
    WorkspaceLayout,
    ProjectLayout,
    NodeLayout,
    ConnectionLayout,
    PortPosition,
    ConnectionStyle
)
from config.config_loader import get as _get_config

_NODE_DEFAULT_WIDTH = _get_config("node_default_width", 80.0)
_NODE_DEFAULT_HEIGHT = _get_config("node_default_height", 40.0)
_GRID_MINOR_SIZE = _get_config("grid_minor_size", 20)
_GRID_MAJOR_SIZE = _get_config("grid_major_size", 80)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be used as a directory name.
    
    Replaces invalid characters (for Windows, Linux, macOS filesystems)
    with underscores. Also trims whitespace and limits length.
    
    Args:
        filename: The filename to sanitize (with or without extension)
        
    Returns:
        A safe string for use as a directory name
    """
    # Characters invalid on Windows, Linux, or macOS
    invalid_chars = r'[<>:"\/|?*\x00-\x1f]'
    # Replace invalid characters with underscore
    safe_name = re.sub(invalid_chars, '_', filename)
    # Remove leading/trailing whitespace and dots
    safe_name = safe_name.strip().strip('.')
    # If empty after sanitization, use a default
    if not safe_name:
        safe_name = "untitled"
    # Limit length to avoid filesystem issues (100 chars is safe for most FS)
    if len(safe_name) > 100:
        safe_name = safe_name[:100]
    return safe_name


class LayoutService:
    """
    Service for managing the persistence of workspace layouts.
    
    Layouts are stored in JSON files in a subdirectory named after the project file.
    Each layout file corresponds to a specific narrative map within a project.
    
    Directory structure:
        {project_file_dir}/
        └── {project_file_stem}/
            └── layouts/
                ├── {narrative_map_id}.json   (per-map workspace layouts)
                └── project.json               (project-level layout, RG067)

    Example:
        /user/docs/my_project.json
        /user/docs/my_project/layouts/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv.json
        /user/docs/my_project/layouts/project.json
    """
    
    # Subdirectory name for layouts within project directory
    LAYOUT_SUBDIR = "layouts"

    # Project-level layout file (RG067): agents belong to the project, so
    # their card positions live in a project file, not in a per-map layout
    PROJECT_LAYOUT_FILENAME = "project.json"
    
    @classmethod
    def _get_project_dir(cls, project_filepath: str) -> Path:
        """
        Get the directory for a project based on its filepath.

        The project directory is named after the project file (without extension).
        Example: "/path/to/my_project.json" -> "/path/to/my_project/"

        The same directory is reused across save/load cycles so that layout
        files are always found in the same place.

        Args:
            project_filepath: Full path to the project JSON file

        Returns:
            Path to the project directory (created by caller if needed)
        """
        filepath = Path(project_filepath).resolve()
        base_dir = filepath.parent
        safe_stem = sanitize_filename(filepath.stem)

        return base_dir / safe_stem

    @classmethod
    def _get_layout_dir(cls, project_filepath: str) -> Path:
        """
        Get the layouts directory for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            Path to the layouts directory (created if it doesn't exist)
        """
        project_dir = cls._get_project_dir(project_filepath)
        layout_dir = project_dir / cls.LAYOUT_SUBDIR
        layout_dir.mkdir(parents=True, exist_ok=True)
        return layout_dir

    @classmethod
    def _get_layout_filepath(
        cls, 
        project_filepath: str,
        narrative_map_id: str
    ) -> Path:
        """
        Generate the filepath for a workspace layout.
        
        New structure: {project_dir}/{stem}/layouts/{narrative_map_id}.json
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            
        Returns:
            Path to the layout JSON file
        """
        layout_dir = cls._get_layout_dir(project_filepath)
        safe_map_id = narrative_map_id.replace("/", "_").replace("\\", "_")
        return layout_dir / f"{safe_map_id}.json"

    @classmethod
    def _get_project_layout_filepath(cls, project_filepath: str) -> Path:
        """
        Generate the filepath of the project-level layout (RG067).

        Structure: {project_dir}/layouts/project.json

        Args:
            project_filepath: Full path to the project JSON file

        Returns:
            Path to the project layout JSON file
        """
        return cls._get_layout_dir(project_filepath) / cls.PROJECT_LAYOUT_FILENAME

    @classmethod
    def save_project_layout(
        cls,
        project_filepath: str,
        layout: ProjectLayout
    ) -> bool:
        """
        Save the project-level layout (agent card positions, RG067) to a
        JSON file next to the per-map workspace layouts.

        Args:
            project_filepath: Full path to the project JSON file
            layout: ProjectLayout instance to save

        Returns:
            True if the layout was saved successfully, False otherwise

        Raises:
            ValueError: If project_filepath is empty
            IOError: If the file cannot be written
        """
        if not project_filepath:
            raise ValueError("project_filepath cannot be empty")

        filepath = cls._get_project_layout_filepath(project_filepath)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    layout.to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            return True
        except IOError as e:
            logger.error("Error saving project layout to %s: %s", filepath, e)
            return False

    @classmethod
    def load_project_layout(
        cls,
        project_filepath: str
    ) -> Optional[ProjectLayout]:
        """
        Load the project-level layout (RG067) from its JSON file.

        Args:
            project_filepath: Full path to the project JSON file

        Returns:
            ProjectLayout instance if the file exists and is valid,
            None otherwise
        """
        filepath = cls._get_project_layout_filepath(project_filepath)

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProjectLayout.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError) as e:
            logger.error("Error loading project layout from %s: %s", filepath, e)
            return None


    @classmethod
    def save_workspace_layout(
        cls,
        project_filepath: str,
        narrative_map_id: str,
        layout: WorkspaceLayout
    ) -> bool:
        """
        Save a workspace layout to a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            layout: WorkspaceLayout instance to save
            
        Returns:
            True if the layout was saved successfully, False otherwise
            
        Raises:
            ValueError: If project_filepath is empty or narrative_map_id is empty
            IOError: If the file cannot be written
        """
        if not project_filepath:
            raise ValueError("project_filepath cannot be empty")
        if not narrative_map_id:
            raise ValueError("narrative_map_id cannot be empty")
        
        filepath = cls._get_layout_filepath(project_filepath, narrative_map_id)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    layout.to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            return True
        except IOError as e:
            logger.error("Error saving layout to %s: %s", filepath, e)
            return False

    @classmethod
    def load_workspace_layout(
        cls,
        project_filepath: str,
        narrative_map_id: str
    ) -> Optional[WorkspaceLayout]:
        """
        Load a workspace layout from a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            
        Returns:
            WorkspaceLayout instance if the file exists and is valid,
            None otherwise
        """
        filepath = cls._get_layout_filepath(project_filepath, narrative_map_id)
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return WorkspaceLayout.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError) as e:
            logger.error("Error loading layout from %s: %s", filepath, e)
            return None


    @classmethod
    def snap_to_grid(cls, value: float, grid_size: float = None, offset: float = 0.0) -> float:
        """
        Snap a coordinate value to the nearest grid step (RG046).

        Args:
            value: The coordinate to snap
            grid_size: Grid step in pixels (defaults to grid_minor_size from config)
            offset: Origin of the grid (TSK31): the grid lines are at
                offset + k * grid_size; 0 by default (other views unchanged)

        Returns:
            The snapped coordinate
        """
        if grid_size is None:
            grid_size = _GRID_MINOR_SIZE
        if grid_size <= 0:
            return value
        return round((value - offset) / grid_size) * grid_size + offset

    @staticmethod
    def _rects_overlap(x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        """Check whether two rectangles overlap."""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or
                    y1 + h1 <= y2 or y2 + h2 <= y1)

    @classmethod
    def find_non_overlapping_position(
        cls,
        x: float,
        y: float,
        width: float,
        height: float,
        existing_rects: list
    ) -> tuple:
        """
        Find a position that does not overlap any existing rectangle (RG050).

        Starting from (x, y), applies lateral translations of grid_major_size
        until a free spot is found. If the horizontal scan exceeds a reasonable
        limit, moves down by grid_major_size and resets x.

        Args:
            x: Initial x position (already snapped to grid)
            y: Initial y position (already snapped to grid)
            width: Width of the new node
            height: Height of the new node
            existing_rects: List of tuples (x, y, width, height) for existing nodes

        Returns:
            Tuple (adjusted_x, adjusted_y) that does not overlap any existing rect
        """
        if not existing_rects:
            return x, y

        step = _GRID_MAJOR_SIZE
        max_attempts = 200  # Safety limit to avoid infinite loops
        current_x = x
        current_y = y

        for _ in range(max_attempts):
            collision = False
            for ex, ey, ew, eh in existing_rects:
                if cls._rects_overlap(current_x, current_y, width, height,
                                      ex, ey, ew, eh):
                    collision = True
                    break
            if not collision:
                return current_x, current_y
            # Move right by one grid major step
            current_x += step

        # If horizontal scan failed, move down and retry
        current_x = x
        current_y += step
        for _ in range(max_attempts):
            collision = False
            for ex, ey, ew, eh in existing_rects:
                if cls._rects_overlap(current_x, current_y, width, height,
                                      ex, ey, ew, eh):
                    collision = True
                    break
            if not collision:
                return current_x, current_y
            current_x += step

        return current_x, current_y

    @classmethod
    def find_first_free_cell(
        cls,
        x: float,
        y: float,
        width: float,
        height: float,
        existing_rects: list,
        step_x: float,
        step_y: float,
        bounds: tuple = None,
        max_cells: int = 10000
    ) -> tuple:
        """
        Find the first free cell of a grid (steps step_x x step_y, anchored on
        (x, y)), scanned row by row from the top-left corner (TSK30).

        Args:
            x: X of the grid origin (first column)
            y: Y of the grid origin (first row)
            width: Width of the item to place
            height: Height of the item to place
            existing_rects: List of tuples (x, y, width, height) for existing items
            step_x: Horizontal cell size
            step_y: Vertical cell size
            bounds: Optional (left, top, right, bottom) the item rect must fit in
            max_cells: Safety limit on the scanned cells

        Returns:
            Tuple (cell_x, cell_y) of the first free cell, (x, y) if none found
        """
        if bounds is not None:
            left, top, right, bottom = bounds
        else:
            left, top = x, y
            right, bottom = x + max_cells * step_x, y + max_cells * step_y
        scanned = 0
        cy = y
        while cy + height <= bottom and scanned < max_cells:
            cx = x
            while cx + width <= right and scanned < max_cells:
                if cx >= left and cy >= top and not any(
                        cls._rects_overlap(cx, cy, width, height, ex, ey, ew, eh)
                        for ex, ey, ew, eh in existing_rects):
                    return cx, cy
                cx += step_x
                scanned += 1
            cy += step_y
        return x, y

    @classmethod
    def find_nearest_free_position(
        cls,
        x: float,
        y: float,
        width: float,
        height: float,
        existing_rects: list,
        step_x: float,
        step_y: float,
        bounds: tuple = None,
        max_radius: int = 50
    ) -> tuple:
        """
        Find the nearest grid-aligned free position (RG050, RG065 cells).

        Scans the cells of a grid (steps step_x x step_y, anchored on (x, y))
        ring by ring, in order of increasing Chebyshev distance from (x, y),
        and returns the first cell whose rectangle fits within bounds and
        does not overlap any existing rectangle.

        Args:
            x: Initial x position (already snapped to the cell grid)
            y: Initial y position (already snapped to the cell grid)
            width: Width of the item to place
            height: Height of the item to place
            existing_rects: List of tuples (x, y, width, height) for existing items
            step_x: Horizontal cell size
            step_y: Vertical cell size
            bounds: Optional (left, top, right, bottom) the item rect must fit in
            max_radius: Safety limit on the ring scan

        Returns:
            Tuple (adjusted_x, adjusted_y) on a free cell
        """
        if not existing_rects:
            return x, y

        for radius in range(max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if max(abs(dx), abs(dy)) != radius:
                        continue
                    cx = x + dx * step_x
                    cy = y + dy * step_y
                    if bounds is not None:
                        left, top, right, bottom = bounds
                        if cx < left or cy < top or cx + width > right or cy + height > bottom:
                            continue
                    if not any(cls._rects_overlap(cx, cy, width, height,
                                                  ex, ey, ew, eh)
                               for ex, ey, ew, eh in existing_rects):
                        return cx, cy

        return x, y

    @classmethod
    def create_node_layout(
        cls,
        node_id: int,
        node_type: str,
        x: float = 100.0,
        y: float = 100.0,
        width: float = _NODE_DEFAULT_WIDTH,
        height: float = _NODE_DEFAULT_HEIGHT
    ) -> NodeLayout:
        """
        Factory method to create a NodeLayout with sensible defaults.

        Args:
            node_id: The business entity ID
            node_type: The type of the node (string from BlockType enum)
            x: X position (default: 100.0)
            y: Y position (default: 100.0)
            width: Node width (default: from config.json)
            height: Node height (default: from config.json)
            
        Returns:
            A new NodeLayout instance
            
        Raises:
            ValueError: If node_type is not a valid BlockType
        """
        from core.models.view_model import BlockType
        
        try:
            node_type_enum = BlockType(node_type)
        except ValueError:
            raise ValueError(f"Invalid node_type: {node_type}. Must be one of {list(BlockType)}")

        # RG046: snap coordinates to the grid
        x = cls.snap_to_grid(x)
        y = cls.snap_to_grid(y)

        return NodeLayout(
            node_id=node_id,
            node_type=node_type_enum,
            x=x,
            y=y,
            width=width,
            height=height
        )

    @classmethod
    def create_connection_layout(
        cls,
        source_node_id: int,
        target_node_id: int,
        relation_id: int = None,
    ) -> ConnectionLayout:
        """
        Factory method to create a ConnectionLayout with sensible defaults.

        Args:
            source_node_id: Business entity ID of the source block
            target_node_id: Business entity ID of the target block
            relation_id: Business entity ID of the transition (Transition.id)

        Returns:
            A new ConnectionLayout instance (directed arrow by default)
        """
        return ConnectionLayout(
            source_node_id=source_node_id,
            source_port=PortPosition.RIGHT,
            target_node_id=target_node_id,
            target_port=PortPosition.LEFT,
            style=ConnectionStyle.ARROW,
            color=None,
            thickness=2.0,
            relation_id=relation_id,
        )

