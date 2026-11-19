# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : relationship_service.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Agent-agent relationship business logic (RG035, FN034/FN037, TSK20).

RG035 (hardened session 06): a relationship is binary (exactly two DISTINCT
agents - no self-relationship - unordered pair stored canonically sorted,
TSK25), non-directed and typed (the type is read from the configuration file
value list, FN037), anchored to exactly one block; there can be only one
relationship per (block, agent pair) - the block/relationship link is unique
for the MVP. No Qt dependency (RG058).
"""

from typing import List, Optional, Tuple

from config.config_loader import get as _get_config
from core.models.data_model import NarrativeMap, Relationship


class RelationshipService:
    """Pure business logic on relationships; no Qt dependency (RG058)."""

    @staticmethod
    def relationship_types() -> List[str]:
        """FN037: the configurable list of relationship types (config.json)."""
        return list(_get_config("relationship_types", []))

    @staticmethod
    def validate_type(typ: str) -> bool:
        """FN037: a relationship type must belong to the configured list."""
        return typ in RelationshipService.relationship_types()

    @staticmethod
    def canonical_pair(agent_1_id: int, agent_2_id: int) -> Tuple[int, int]:
        """TSK25: unordered pair, canonical sorted storage (smaller id first)."""
        return (agent_1_id, agent_2_id) if agent_1_id < agent_2_id else (agent_2_id, agent_1_id)

    @staticmethod
    def check_pair(agent_1_id: int, agent_2_id: int) -> None:
        """RG035: the two agents of a relationship are distinct (no self-relationship)."""
        if agent_1_id == agent_2_id:
            raise ValueError("A relationship links two distinct agents (RG035)")

    @staticmethod
    def find_relationship(narrative_map: NarrativeMap, block_id: int,
                          agent_1_id: int, agent_2_id: int) -> Optional[Relationship]:
        """RG035: the unique relationship of the (block, agent pair), or None."""
        a, b = RelationshipService.canonical_pair(agent_1_id, agent_2_id)
        for r in narrative_map.relationship:
            if r.block_id == block_id and r.agent_1_id == a and r.agent_2_id == b:
                return r
        return None

    @staticmethod
    def get_block_relationships(narrative_map: NarrativeMap, block_id: int) -> List[Relationship]:
        """All the relationships anchored to a block (RG041: membership derives from the anchor)."""
        return [r for r in narrative_map.relationship if r.block_id == block_id]

    @staticmethod
    def get_pair_relationships(narrative_map: NarrativeMap,
                               agent_1_id: int, agent_2_id: int) -> List[Relationship]:
        """All the relationships of an agent pair (its history), across the map."""
        a, b = RelationshipService.canonical_pair(agent_1_id, agent_2_id)
        return [r for r in narrative_map.relationship
                if {r.agent_1_id, r.agent_2_id} == {a, b}]

    @staticmethod
    def block_min_rank(narrative_map: NarrativeMap, block_id: int) -> int:
        """Minimum rank of a block across all journeys (its journey_node
        sequence_order values, RG044); 0 when the block has no attachment."""
        ranks = [jn.sequence_order for jn in narrative_map.journey_node
                 if jn.block_id == block_id]
        return min(ranks) if ranks else 0

    @staticmethod
    def ordered_anchor_block_ids(narrative_map: NarrativeMap) -> List[int]:
        """Block ids ordered by minimum rank across all journeys (ties by block
        id) - the RG069 ordering rule, shared by the "Relationships" view side
        panel and the anchor block list of the relationship dialog."""
        return sorted((b.id for b in narrative_map.block),
                      key=lambda bid: (RelationshipService.block_min_rank(narrative_map, bid), bid))

    @staticmethod
    def pair_state_at_block(narrative_map: NarrativeMap, agent_1_id: int, agent_2_id: int,
                            block_id: int) -> Optional[Relationship]:
        """RG069/SU011: the state of an agent pair at a given block = the
        relationship anchored to the last block of rank lower than or equal to
        the block's rank (ranks = minimum across all journeys). Derived data,
        never stored. With RG035 (unique (block, pair)) at most one
        relationship per (block, pair), so the result is unambiguous."""
        threshold = RelationshipService.block_min_rank(narrative_map, block_id)
        best = None
        best_rank = -1
        for r in RelationshipService.get_pair_relationships(narrative_map, agent_1_id, agent_2_id):
            rank = RelationshipService.block_min_rank(narrative_map, r.block_id)
            if rank <= threshold and rank > best_rank:
                best, best_rank = r, rank
        return best
