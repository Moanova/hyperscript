# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : journey_sequence_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Reading sequence of journeys (RG044, TSK08).

The reading sequence of a journey is a DFS from the unique Start block
(RG025), following only the transitions of the journey (both endpoints
attached to it - RG041), branches explored by increasing transition id,
cycles memoized, and attached but unreachable blocks ranked deterministically
(by block id) after the reachable ones. The rank of each block is recomputed
on every graph modification and when the project is loaded, and is never
editable manually (RG044).
"""

from core.models.data_model import NarrativeMap


class JourneySequenceService:
    """Pure computation of journey_node.sequence_order; no Qt dependency."""

    @staticmethod
    def recompute_all(narrative_map: NarrativeMap) -> None:
        """Recompute the sequence of every journey of the map (RG044)."""
        for journey in narrative_map.journey:
            JourneySequenceService.recompute_journey(narrative_map, journey.id)

    @staticmethod
    def recompute_journey(narrative_map: NarrativeMap, journey_id: int) -> None:
        """Recompute sequence_order for the journey nodes of one journey (RG044)."""
        attached = {jn.block_id for jn in narrative_map.journey_node if jn.journey_id == journey_id}
        start = next((b for b in narrative_map.block if b.typ == "Start"), None)  # RG025
        order = {}
        if start is not None and start.id in attached:
            visited = set()

            def visit(block_id: int) -> None:
                if block_id in visited:
                    return
                visited.add(block_id)
                order[block_id] = len(order)
                outgoing = sorted(
                    (t for t in narrative_map.transition
                     if t.from_block_id == block_id and t.to_block_id in attached),
                    key=lambda t: t.id,
                )
                for t in outgoing:
                    visit(t.to_block_id)

            visit(start.id)
        # Deterministic fallback for attached but unreachable blocks (RG044)
        for b in sorted(narrative_map.block, key=lambda b: b.id):
            if b.id in attached and b.id not in order:
                order[b.id] = len(order)
        for jn in narrative_map.journey_node:
            if jn.journey_id == journey_id:
                jn.sequence_order = order.get(jn.block_id, 0)
