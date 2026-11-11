# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : journey_filter_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Journey filter visibility (RG041/RG048, TSK08).

RG048/FN029: the journey filter shows either all journeys or a single one,
in all views. With the filter active, only the blocks of the active journey,
the transitions whose two blocks belong to it, and the participations /
relationships whose anchor block belongs to it stay fully visible; the other
elements are dimmed (opacity from config.json) and non-interactive.
RG041: membership is derived - a transition belongs to a journey iff both its
endpoints do; a participation or relationship iff its anchor block does.
The filter is disabled by default when a project is opened, is not persisted
between sessions and does not mark the map as modified (RG047).
"""

from typing import Optional, Set

from config.config_loader import get as _get_config
from core.models.data_model import NarrativeMap


class JourneyFilterService:
    """Pure visibility computation for the journey filter; no Qt dependency."""

    @staticmethod
    def filter_opacity() -> float:
        """RG048/RG059: dimmed opacity is read from config.json."""
        return float(_get_config("journey_filter_opacity", 0.25))

    @staticmethod
    def visible_block_ids(narrative_map: NarrativeMap, journey_id: Optional[int] = None) -> Set[int]:
        """None = filter off: all blocks. Otherwise only the journey's blocks."""
        if journey_id is None:
            return {b.id for b in narrative_map.block}
        return {jn.block_id for jn in narrative_map.journey_node if jn.journey_id == journey_id}

    @staticmethod
    def visible_transition_ids(narrative_map: NarrativeMap, journey_id: Optional[int] = None) -> Set[int]:
        """RG041: a transition is visible iff both its endpoints are."""
        vis = JourneyFilterService.visible_block_ids(narrative_map, journey_id)
        return {t.id for t in narrative_map.transition
                if t.from_block_id in vis and t.to_block_id in vis}

    @staticmethod
    def visible_participation_ids(narrative_map: NarrativeMap, journey_id: Optional[int] = None) -> Set[int]:
        """RG041: a participation is visible iff its anchor block is."""
        vis = JourneyFilterService.visible_block_ids(narrative_map, journey_id)
        return {p.id for p in narrative_map.participation if p.block_id in vis}

    @staticmethod
    def visible_relationship_ids(narrative_map: NarrativeMap, journey_id: Optional[int] = None) -> Set[int]:
        """RG041: a relationship is visible iff its anchor block is."""
        vis = JourneyFilterService.visible_block_ids(narrative_map, journey_id)
        return {r.id for r in narrative_map.relationship if r.block_id in vis}
