# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agent_filter_service.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Agent filter visibility (RG063/RG064, TSK19a).

RG063/FN039: the agent filter shows, in the views bearing on the narrative map
(not the "Agents" view - project-level agents), either all elements or only
the blocks the agent participates in; a transition is visible iff both its
endpoints are; a participation/relationship iff its anchor block is (RG041).
Other elements are dimmed (same opacity as the journey filter, config.json)
and non-interactive. The filter is disabled by default, not persisted (RG047)
and does not mark anything as modified.
RG064: with the journey filter also active, the intersection of the two
filters applies (computed by the caller from the two visible-id sets).
"""

from typing import Optional, Set

from core.models.data_model import NarrativeMap
from core.services.journey_filter_service import JourneyFilterService


class AgentFilterService:
    """Pure visibility computation for the agent filter; no Qt dependency."""

    @staticmethod
    def filter_opacity() -> float:
        """RG063: same dimmed opacity as the journey filter (config.json)."""
        return JourneyFilterService.filter_opacity()

    @staticmethod
    def visible_block_ids(narrative_map: NarrativeMap, agent_id: Optional[int] = None) -> Set[int]:
        """None = filter off: all blocks. Otherwise only the blocks the agent
        participates in (RG041: participation membership derives from the block)."""
        if agent_id is None:
            return {b.id for b in narrative_map.block}
        return {p.block_id for p in narrative_map.participation if p.agent_id == agent_id}

    @staticmethod
    def visible_transition_ids(narrative_map: NarrativeMap, agent_id: Optional[int] = None) -> Set[int]:
        """RG041: a transition is visible iff both its endpoints are."""
        vis = AgentFilterService.visible_block_ids(narrative_map, agent_id)
        return {t.id for t in narrative_map.transition
                if t.from_block_id in vis and t.to_block_id in vis}

    @staticmethod
    def visible_participation_ids(narrative_map: NarrativeMap, agent_id: Optional[int] = None) -> Set[int]:
        """RG041: a participation is visible iff its anchor block is."""
        vis = AgentFilterService.visible_block_ids(narrative_map, agent_id)
        return {p.id for p in narrative_map.participation if p.block_id in vis}

    @staticmethod
    def visible_relationship_ids(narrative_map: NarrativeMap, agent_id: Optional[int] = None) -> Set[int]:
        """RG041: a relationship is visible iff its anchor block is."""
        vis = AgentFilterService.visible_block_ids(narrative_map, agent_id)
        return {r.id for r in narrative_map.relationship if r.block_id in vis}
