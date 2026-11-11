# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : journey_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Journey attachment helpers (RG039/RG040/RG041/RG042, TSK08).

Attachment is stored on blocks only (Journey_node), never on transitions
(RG041). No orphan block: every block belongs to at least one journey (RG040).
"""

from typing import List, Optional

from core.models.data_model import Journey, Journey_node, NarrativeMap


class JourneyService:
    """Pure helpers on journey nodes; no Qt dependency."""

    @staticmethod
    def get_default_journey(narrative_map: NarrativeMap) -> Optional[Journey]:
        """RG039: exactly one default journey; fall back to the oldest one."""
        for j in narrative_map.journey:
            if j.default:
                return j
        return narrative_map.journey[0] if narrative_map.journey else None

    @staticmethod
    def attachment_journey_ids(narrative_map: NarrativeMap, block_id: int) -> List[int]:
        return [jn.journey_id for jn in narrative_map.journey_node if jn.block_id == block_id]

    @staticmethod
    def attach_block(narrative_map: NarrativeMap, block_id: int, journey_id: int) -> Journey_node:
        jn = Journey_node(
            id=narrative_map.get_next_id('journey_node'),
            journey_id=journey_id,
            block_id=block_id,
            sequence_order=0,  # placeholder; the real rank is computed by JourneySequenceService (RG044)
        )
        narrative_map.journey_node.append(jn)
        return jn

    @staticmethod
    def attach_new_block(narrative_map: NarrativeMap, block_id: int, filter_active: bool) -> None:
        """RG040: a newly created block is attached to the active journey if the
        journey filter is active, to the default journey otherwise. The filter
        flag is session UI state passed by the caller (never persisted, RG047)."""
        if filter_active:
            journey = narrative_map.get_active_journey()
        else:
            journey = JourneyService.get_default_journey(narrative_map)
        if journey is not None:
            JourneyService.attach_block(narrative_map, block_id, journey.id)

    @staticmethod
    def set_block_attachments(narrative_map: NarrativeMap, block_id: int, journey_ids: List[int]) -> None:
        """RG042: replace the journeys a block is attached to. The list cannot
        be emptied - a block cannot be detached from its last journey."""
        if not journey_ids:
            raise ValueError("A block cannot be detached from its last journey")  # RG042
        current = set(JourneyService.attachment_journey_ids(narrative_map, block_id))
        target = set(journey_ids)
        for jid in current - target:
            narrative_map.journey_node[:] = [
                jn for jn in narrative_map.journey_node
                if not (jn.block_id == block_id and jn.journey_id == jid)
            ]
        for jid in target - current:
            JourneyService.attach_block(narrative_map, block_id, jid)
