# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : transition_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Business rules of transitions between narrative blocks (TSK08).

RG028: chaining is constrained by the block-type matrix below; cycles are
allowed (e.g. Scene -> Pivot -> Condition -> the same Scene); there can be
only one transition per ordered pair of blocks.
RG023: deleting a block cascades to its transitions, participations, anchored
relationships and journey attachments.
RG041: journey membership is derived from the blocks - attachments are stored
on blocks only, never on transitions.
"""

from typing import Dict, List, Optional

from core.models.data_model import Block, NarrativeMap, Transition

# RG028: allowed chaining matrix (source block type -> allowed target types)
ALLOWED_TARGET_TYPES: Dict[str, set] = {
    "Start": {"Scene", "Pivot"},
    "Scene": {"Scene", "Pivot", "End"},
    "Pivot": {"Condition"},
    "Condition": {"Scene", "End"},
    "End": set(),
}


def type_allows_outgoing(block_type: str) -> bool:
    """RG028: the block type may be the source of a transition (outgoing port).
    End has no outgoing transition (empty target set)."""
    return bool(ALLOWED_TARGET_TYPES.get(block_type, set()))


def type_allows_incoming(block_type: str) -> bool:
    """RG025/RG028: the block type may be the target of a transition (incoming
    port). Start is never the target of any transition."""
    return any(block_type in targets for targets in ALLOWED_TARGET_TYPES.values())


class TransitionService:
    """Pure business logic on transitions; no Qt dependency (RG058)."""

    @staticmethod
    def get_block(narrative_map: NarrativeMap, block_id: int) -> Optional[Block]:
        for b in narrative_map.block:
            if b.id == block_id:
                return b
        return None

    @staticmethod
    def has_transition_between(narrative_map: NarrativeMap, from_block_id: int, to_block_id: int) -> bool:
        """RG028: at most one transition per ordered pair of blocks."""
        return any(t.from_block_id == from_block_id and t.to_block_id == to_block_id
                   for t in narrative_map.transition)

    @staticmethod
    def can_create_transition(narrative_map: NarrativeMap, from_block_id: int, to_block_id: int) -> bool:
        """RG028: both blocks must exist, the target type must be allowed for
        the source type (matrix), and the ordered pair must not be linked yet."""
        src = TransitionService.get_block(narrative_map, from_block_id)
        dst = TransitionService.get_block(narrative_map, to_block_id)
        if src is None or dst is None:
            return False
        if dst.typ not in ALLOWED_TARGET_TYPES.get(src.typ, set()):
            return False
        return not TransitionService.has_transition_between(narrative_map, from_block_id, to_block_id)

    @staticmethod
    def create_transition(narrative_map: NarrativeMap, from_block_id: int, to_block_id: int,
                          note: Optional[str] = None) -> Optional[Transition]:
        """Create a directed transition; returns None when RG028 forbids it."""
        if not TransitionService.can_create_transition(narrative_map, from_block_id, to_block_id):
            return None
        transition = Transition(
            id=narrative_map.get_next_id('transition'),
            from_block_id=from_block_id,
            to_block_id=to_block_id,
            note=note,
        )
        narrative_map.transition.append(transition)
        return transition

    @staticmethod
    def delete_transition(narrative_map: NarrativeMap, transition_id: int) -> bool:
        """Delete a transition. RG041: no journey_node references a transition,
        so nothing else is removed."""
        for i, t in enumerate(narrative_map.transition):
            if t.id == transition_id:
                del narrative_map.transition[i]
                return True
        return False

    @staticmethod
    def transitions_from(narrative_map: NarrativeMap, block_id: int) -> List[Transition]:
        return [t for t in narrative_map.transition if t.from_block_id == block_id]

    @staticmethod
    def transitions_to(narrative_map: NarrativeMap, block_id: int) -> List[Transition]:
        return [t for t in narrative_map.transition if t.to_block_id == block_id]

    @staticmethod
    def delete_block_cascade(narrative_map: NarrativeMap, block_id: int) -> Optional[Dict[str, list]]:
        """RG023: delete a block and cascade to its transitions, participations,
        anchored relationships and journey attachments. Returns the removed
        elements (for the information message, FN018), or None if no such block."""
        block = TransitionService.get_block(narrative_map, block_id)
        if block is None:
            return None
        removed = {
            'block': [block],
            'transition': (TransitionService.transitions_from(narrative_map, block_id)
                           + TransitionService.transitions_to(narrative_map, block_id)),
            'participation': [p for p in narrative_map.participation if p.block_id == block_id],
            'relationship': [r for r in narrative_map.relationship if r.block_id == block_id],
            'journey_node': [jn for jn in narrative_map.journey_node if jn.block_id == block_id],
        }
        narrative_map.transition[:] = [t for t in narrative_map.transition
                                       if t.from_block_id != block_id and t.to_block_id != block_id]
        narrative_map.participation[:] = [p for p in narrative_map.participation if p.block_id != block_id]
        narrative_map.relationship[:] = [r for r in narrative_map.relationship if r.block_id != block_id]
        narrative_map.journey_node[:] = [jn for jn in narrative_map.journey_node if jn.block_id != block_id]
        narrative_map.block.remove(block)
        return removed
