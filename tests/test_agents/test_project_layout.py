# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_project_layout.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the project-level layout (TSK19b, RG067): AgentCardLayout /
ProjectLayout serialization and LayoutService.save_project_layout /
load_project_layout (layouts/project.json), plus the dot-grid snap (RG065)
and the exclusion of project.json from the per-map layout listings."""

import json

from core.models.view_model import AgentCardLayout, ProjectLayout
from core.services.layout_service import LayoutService
from config.config_loader import get as _get_config


def test_agent_card_layout_roundtrip():
    card = AgentCardLayout(agent_id=3, x=120.0, y=240.0, width=160.0, height=100.0, selected=True)
    data = card.to_dict()
    restored = AgentCardLayout.from_dict(data)
    assert restored.agent_id == 3
    assert restored.x == 120.0 and restored.y == 240.0
    assert restored.width == 160.0 and restored.height == 100.0
    assert restored.selected is True


def test_agent_card_layout_defaults_from_config():
    card = AgentCardLayout(agent_id=1, x=0.0, y=0.0)
    assert card.width == _get_config("agents_view_card_width", 160.0)
    assert card.height == _get_config("agents_view_card_height", 100.0)
    assert card.selected is False


def test_project_layout_roundtrip():
    layout = ProjectLayout()
    layout.add_agent_card(AgentCardLayout(agent_id=1, x=20.0, y=40.0))
    layout.add_agent_card(AgentCardLayout(agent_id=2, x=200.0, y=60.0))
    restored = ProjectLayout.from_dict(json.loads(json.dumps(layout.to_dict())))
    assert set(restored.agent_cards.keys()) == {1, 2}
    assert restored.get_agent_card_layout(2).x == 200.0
    assert restored.get_agent_card_layout(99) is None
    assert layout.remove_agent_card(1) is True
    assert layout.remove_agent_card(1) is False
    assert set(layout.agent_cards.keys()) == {2}


def test_project_layout_save_load_roundtrip(tmp_path):
    project_file = str(tmp_path / "myproj.json")
    layout = ProjectLayout()
    layout.add_agent_card(AgentCardLayout(agent_id=7, x=80.0, y=160.0))

    assert LayoutService.save_project_layout(project_file, layout) is True
    layout_file = tmp_path / "myproj" / "layouts" / "project.json"
    assert layout_file.exists()

    restored = LayoutService.load_project_layout(project_file)
    assert restored is not None
    card = restored.get_agent_card_layout(7)
    assert card is not None and card.x == 80.0 and card.y == 160.0


def test_load_project_layout_missing_file_returns_none(tmp_path):
    project_file = str(tmp_path / "nope.json")
    assert LayoutService.load_project_layout(project_file) is None


def test_project_layout_file_excluded_from_map_layouts(tmp_path):
    """project.json (RG067) must not be listed as a narrative-map layout,
    and must survive delete_stale_layouts."""
    project_file = str(tmp_path / "myproj.json")
    LayoutService.save_workspace_layout(
        project_file, "map-uuid-1",
        LayoutService.create_empty_layout("map-uuid-1"))
    LayoutService.save_project_layout(project_file, ProjectLayout())

    listed = LayoutService.list_project_layouts(project_file)
    assert "map-uuid-1" in listed
    assert "project" not in listed

    deleted = LayoutService.delete_stale_layouts(project_file, keep_ids=["map-uuid-1"])
    assert deleted == 0
    layout_dir = tmp_path / "myproj" / "layouts"
    assert (layout_dir / "map-uuid-1.json").exists()
    assert (layout_dir / "project.json").exists()


def test_snap_to_dot_grid():
    """RG065: the card position is forced onto the nearest anchor dot
    (agents_view_dot_spacing_px as grid step)."""
    spacing = float(_get_config("agents_view_dot_spacing_px", 20))
    assert LayoutService.snap_to_grid(23.0, grid_size=spacing) == 20.0
    assert LayoutService.snap_to_grid(31.0, grid_size=spacing) == 40.0
    assert LayoutService.snap_to_grid(80.0, grid_size=spacing) == 80.0
